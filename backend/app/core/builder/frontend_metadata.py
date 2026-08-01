import json
import os

def export_frontend_metadata(manifest_path: str, output_dir: str):
    output_path = os.path.join(output_dir, "metadata.json")
    
    if os.path.exists(output_path):
        return
    
    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    meta = manifest["meta"]

    frontend_metadata = {
        "region": meta["region"],
        "categories": meta["amenities"],
        "modes": meta["modes"],
        "kernel": meta["kernel_params"],
        "cutoff": meta["cutoff"],
        "ceiling": meta["ceiling"],
        "schema_version": manifest["schema_version"]
    }

    with open(output_path, "w") as f:
        json.dump(frontend_metadata, f, indent=2)