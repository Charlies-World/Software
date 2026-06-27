import argparse, json, shutil
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageOps, ImageDraw

EXTS={'.png','.jpg','.jpeg','.webp'}

def direction(path):
    d=json.loads(Path(path).read_text())
    assert d.get('name')
    return d

def images(folder):
    return sorted(p for p in Path(folder).rglob('*') if p.suffix.lower() in EXTS)

def clean_image(src, out, d):
    im=ImageOps.exif_transpose(Image.open(src)).convert('RGBA')
    pix=im.load(); tol=int(d['background'].get('near_white_tolerance',18))
    for y in range(im.height):
        for x in range(im.width):
            r,g,b,a=pix[x,y]
            if a>240 and abs(r-255)<=tol and abs(g-255)<=tol and abs(b-255)<=tol:
                pix[x,y]=(255,255,255,255)
    im=im.convert('RGB')
    target=int(d.get('canvas',{}).get('target_size',1500))
    if target: im=im.resize((target,target))
    out.parent.mkdir(parents=True,exist_ok=True)
    im.save(out)

def sheet(paths, out):
    out.parent.mkdir(parents=True,exist_ok=True)
    board=Image.new('RGB',(600,200),'white')
    draw=ImageDraw.Draw(board); draw.text((10,10),f'{len(paths)} outputs',fill=(0,0,0))
    board.save(out)

def run(inp, direc, out):
    d=direction(direc); out=Path(out); rec=[]; outs=[]
    for src in images(inp):
        dest=out/'accepted'/f'{src.stem}.clean.png'
        clean_image(src,dest,d); outs.append(dest)
        rec.append({'source_path':str(src),'status':'accepted','output_path':str(dest)})
    (out/'reports').mkdir(parents=True,exist_ok=True)
    (out/'reports'/'manifest.json').write_text(json.dumps({'tool':'SoftStrange-ImageEditor','summary':{'total':len(rec),'accepted':len(rec),'review':0,'rejected':0},'images':rec},indent=2))
    (out/'reports'/'summary.md').write_text(f"# Image run summary\n\n- Total: {len(rec)}\n- Accepted: {len(rec)}\n")
    sheet(outs,out/'previews'/'contact-sheet.png')
    return {'total':len(rec),'accepted':len(rec)}

def repo_process(repo_root,input_folder,direction_path,pipeline_root):
    repo=Path(repo_root); run_id=datetime.utcnow().strftime('run-%Y%m%d-%H%M%S')
    pipeline=repo/pipeline_root; processing=pipeline/'processing'/run_id
    summary=run(repo/input_folder,repo/direction_path,processing)
    for f in (processing/'accepted').glob('*.png'):
        dst=pipeline/'processed'/'accepted'/f.name; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(f,dst)
    archive=pipeline/'archive'/'originals'/run_id; archive.mkdir(parents=True,exist_ok=True)
    for f in images(repo/input_folder): shutil.move(str(f),archive/f.name)
    reports=pipeline/'reports'/run_id; shutil.copytree(processing/'reports',reports,dirs_exist_ok=True)
    previews=pipeline/'previews'/run_id; shutil.copytree(processing/'previews',previews,dirs_exist_ok=True)
    print(json.dumps({'run_id':run_id,'summary':summary},indent=2))

def main(argv=None):
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('validate-direction'); a.add_argument('--direction',required=True)
    a=sub.add_parser('run'); a.add_argument('--input',required=True); a.add_argument('--direction',required=True); a.add_argument('--output',required=True)
    a=sub.add_parser('repo-process'); a.add_argument('--repo-root',default='.'); a.add_argument('--input-folder',required=True); a.add_argument('--direction',required=True); a.add_argument('--pipeline-root',default='image-pipeline')
    args=p.parse_args(argv)
    if args.cmd=='validate-direction': print(json.dumps({'ok':True,'name':direction(args.direction)['name']})); return 0
    if args.cmd=='run': print(json.dumps(run(args.input,args.direction,args.output),indent=2)); return 0
    if args.cmd=='repo-process': repo_process(args.repo_root,args.input_folder,args.direction,args.pipeline_root); return 0
if __name__=='__main__': raise SystemExit(main())
