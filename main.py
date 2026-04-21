from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rdkit import Chem
from rdkit.Chem import rdDetermineBonds
from rdkit.Chem import rdDepictor
from rdkit.Chem.Draw import rdMolDraw2D

app = FastAPI(title="XYZ to Molecule API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class XYZRequest(BaseModel):
    xyz_data: str

@app.post("/api/convert-xyz")
async def convert_xyz_to_mol(request: XYZRequest):
    try:
        # 1. Parse the raw XYZ text
        raw_mol = Chem.MolFromXYZBlock(request.xyz_data)
        if raw_mol is None:
            raise ValueError("Invalid XYZ data provided.")

        # 2. Attempt strict bond perception (Connectivity + Bond Orders)
        try:
            rdDetermineBonds.DetermineBonds(raw_mol)
        except ValueError as e:
            print(f"Strict bond determination failed: {e}. Falling back to single-bond connectivity.")
            raw_mol = Chem.MolFromXYZBlock(request.xyz_data) 
            rdDetermineBonds.DetermineConnectivity(raw_mol)

        # 3. Create a copy for 2D representation
        mol_2d = Chem.Mol(raw_mol)

        # 4. Compute 2D coordinates 
        rdDepictor.Compute2DCoords(mol_2d)

        # 5. Generate the SVG string
        drawer = rdMolDraw2D.MolDraw2DSVG(400, 400)
        opts = drawer.drawOptions()
        opts.clearBackground = False 
        
        drawer.DrawMolecule(mol_2d)
        drawer.FinishDrawing()
        svg_string = drawer.GetDrawingText()

        # 6. Generate the standard MolBlock
        mol_block = Chem.MolToMolBlock(mol_2d)

        return {
            "svg": svg_string,
            "mol_block": mol_block,
            "success": True
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))