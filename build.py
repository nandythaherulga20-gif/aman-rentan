import os
import re

def read_template():
    template_path = os.path.join('src', 'template.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def replace_version(template, version):
    return template.replace('{{VERSION}}', version)

def replace_asisten_function(template, version):
    # Define the asisten function for each version
    if version == 'RENTAN':
        asisten_func = '''// ASISTEN_FUNCTION_START
window.asisten = async function (pesan, konteks, model) {
    // Combine prompt, message, and all data (from syntheticData) into one text
    const prompt = "Anda adalah asisten kampus yang membantu dengan kantin, diskusi, rekap data, dan jadwal.";
    const combined = prompt + "\\nPesan: " + pesan + "\\nKonteks: " + konteks;

    // If model is provided, we use it (simulate by calling a mock model function)
    let balasan = "";
    let aksi = [];

    if (model) {
        // Simulate calling the model with the combined prompt
        balasan = "Model menjalani: " + combined;
        // Check if the user's pesan contains a request for AKSI (for demonstration)
        if (pesan.includes("AKSI")) {
            // Simulate the model returning an AKSI line
            balasan += "\\nAKSI {\"tool\": \"example_tool\", \"params\": {}}";
        }
    } else {
        // Fallback to original LLM (simulated as a simple response)
        balasan = "Asisten kampus: Saya sedang membantu Anda.";
    }

    // Parse AKSI lines from the balasan (if any) and execute them immediately in rentan version
    const aksimatch = balasan.match(/AKSI\\s*(\\{.*\\})/g);
    if (aksimatch) {
        for (const match of aksimatch) {
            try {
                const jsonStr = match.match(/\\{.*\\}/)[0];
                const actionObj = JSON.parse(jsonStr);
                aksi.push({ 
                    tool: actionObj.tool || "unknown_tool", 
                    status: "dijalankan", 
                    ref: Math.random().toString(36).substr(2, 9) 
                });
            } catch (e) {
                // If JSON is invalid, ignore
            }
        }
        // Remove the AKSI lines from the balasan for display? The spec doesn't specify, but we'll keep them in the balasan for transparency.
    }

    return { balasan, aksi };
};
// ASISTEN_FUNCTION_END'''
    else:  # AMAN
        asisten_func = '''// ASISTEN_FUNCTION_START
window.asisten = async function (pesan, konteks, model) {
    // In aman version, we do not combine all data. We only use the konteks as provided (which should be minimized).
    // We also do not trust the model's output for actions.

    // First, we simulate the model call (if model provided) to get a raw response.
    let rawBalasan = "";
    if (model) {
        // Simulate model: same as rentan but we will not execute actions from it.
        const prompt = "Anda adalah asisten kampus yang membantu dengan kantin, diskusi, rekap data, dan jadwal.";
        const combined = prompt + "\\nPesan: " + pesan + "\\nKonteks: " + konteks;
        rawBalasan = "Model menjalani: " + combined;
        if (pesan.includes("AKSI")) {
            rawBalasan += "\\nAKSI {\"tool\": \"example_tool\", \"params\": {}}";
        }
    } else {
        rawBalasan = "Asisten kampus: Saya sedang membantu Anda.";
    }

    // Now, we process the rawBalasan to:
    // 1. Quarantine and log any untrusted content (in this case, we consider the model output as untrusted)
    // 2. Escape HTML and filter out sensitive information (phone numbers, addresses, and lines with "AKSI")
    // 3. Extract any AKSI lines and decide based on allowlist and role.

    // Define an allowlist of tools per module (simplified)
    const allowlist = {
        kantin: ["lihat_menu", "pesan_makanan"],
        ringkas: ["ringkas_ulasan"],
        rekap: ["lihat_data_mahasiswa"],
        jadwal: ["lihat_jadwal", "Buat_janji"]
    };

    // Define which actions are impactful (require human approval)
    const impactfulActions = {
        kantin: ["pesan_makanan"],
        ringkas: [],
        rekap: [],
        jadwal: ["Buat_janji"]
    };

    // Step 1: Extract AKSI lines from rawBalasan
    const aksimatch = rawBalasan.match(/AKSI\\s*(\\{.*\\})/g);
    const aksiRequests = [];
    if (aksimatch) {
        for (const match of aksimatch) {
            try {
                const jsonStr = match.match(/\\{.*\\}/)[0];
                const actionObj = JSON.parse(jsonStr);
                aksiRequests.push(actionObj);
            } catch (e) {
                // ignore invalid JSON
            }
        }
    }

    // Step 2: Sanitize the balasan for display
    // Escape HTML and remove lines that contain AKSI (to prevent execution) and remove sensitive patterns.
    let balasan = rawBalasan
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;")
        .replace(/AKSI\\s*\\{.*\\}/g, "[AKSI DIFilter]"); // Remove AKSI lines by replacing with a notice

    // Additionally, we can remove phone numbers and addresses (simplified regex)
    balasan = balasan.replace(/0899-\\d{4}-\\d{4}/g, "[Nomor Telepon Disembunyikan]")
                     .replace(/Jl\\. [^,\\n]+/g, "[Alamat Disembunyikan]");

    // Step 3: Process each action request
    const aksi = [];
    for (const actionReq of aksiRequests) {
        const tool = actionReq.tool;
        // Determine module from konteks (simplified: we assume konteks starts with module name)
        let module = null;
        if (konteks.startsWith("menu:")) module = "kantin";
        else if (konteks.startsWith("ulasan:")) module = "ringkas";
        else if (konteks.startsWith("pendaftar:")) module = "rekap";
        else if (konteks.startsWith("rapat:")) module = "jadwal";

        // Check if the tool is in the allowlist for the module
        let status = "ditolak";
        if (module && allowlist[module] && allowlist[module].includes(tool)) {
            // Check if the action is impactful and requires human approval
            if (impactfulActions[module] && impactfulActions[module].includes(tool)) {
                status = "menunggu_persetujuan";
            } else {
                status = "dijalankan";
            }
        }

        aksi.push({
            tool: tool,
            status: status,
            ref: Math.random().toString(36).substr(2, 9)
        });
    }

    return { balasan, aksi };
};
// ASISTEN_FUNCTION_END'''
    
    # Replace the entire block from start marker to end marker
    # We find the indices and slice to avoid re.sub's backslash escaping issues
    start_marker = '// ASISTEN_FUNCTION_START'
    end_marker = '// ASISTEN_FUNCTION_END'
    
    start_idx = template.find(start_marker)
    end_idx = template.find(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        print(f"Markers not found in template for {version}")
        return template
        
    return template[:start_idx] + asisten_func + template[end_idx + len(end_marker):]

def main():
    # Ensure output directories exist
    os.makedirs('rentan', exist_ok=True)
    os.makedirs('aman', exist_ok=True)
    
    template = read_template()
    
    # Generate RENTAN version
    rentan_template = replace_version(template, 'RENTAN')
    rentan_template = replace_asisten_function(rentan_template, 'RENTAN')
    with open(os.path.join('rentan', 'index.html'), 'w', encoding='utf-8') as f:
        f.write(rentan_template)
    
    # Generate AMAN version
    aman_template = replace_version(template, 'AMAN')
    aman_template = replace_asisten_function(aman_template, 'AMAN')
    with open(os.path.join('aman', 'index.html'), 'w', encoding='utf-8') as f:
        f.write(aman_template)
    
    print("Generated rentan/index.html and aman/index.html")

if __name__ == '__main__':
    main()