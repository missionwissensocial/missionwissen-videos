import json,subprocess
sil=[(2.38814,2.85018),(4.70649,5.3671),(6.21782,6.67451),(10.5483,11.0983),(13.0312,13.5343),(17.0476,17.466),(23.7093,24.2299),(27.1724,27.6647),(29.6305,30.0855),(31.9897,32.4854),(33.0657,33.5251),(35.0725,35.6156),(38.6461,39.0157),(41.4641,41.8746),(43.9388,44.5585),(46.8423,47.3509),(52.8303,53.2887),(53.721,54.0283)]
cuts=[(18.40,19.75)]
for s,e in sil:
    if e-s>0.4: cuts.append((round(s+0.15,3),round(e-0.15,3)))
cuts.sort(); json.dump(cuts,open("cuts.json","w"))
# keep segments
dur=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0","vo_raw.mp3"],capture_output=True,text=True).stdout)
keep=[];p=0
for s,e in cuts: keep.append((p,s)); p=e
keep.append((p,dur))
f="".join(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,afade=t=out:st={b-a-0.008:.3f}:d=0.008[k{i}];" for i,(a,b) in enumerate(keep))
f+="".join(f"[k{i}]" for i in range(len(keep)))+f"concat=n={len(keep)}:v=0:a=1[o]"
subprocess.run(["ffmpeg","-y","-v","error","-i","vo_raw.mp3","-filter_complex",f,"-map","[o]","-c:a","libmp3lame","-q:a","2","vo.mp3"],check=True)
def mp(t):
    sh=0
    for s,e in cuts:
        if t>=e: sh+=e-s
        elif t>s: return s-sh
    return t-sh
W=json.load(open("words.json"))
ws=[round(mp(w["start"]),3) for w in W if w["text"] not in ("–","-") and not (18.5<w["start"]<19.6)]
json.dump(ws,open("ws.json","w")); print(len(ws), sum(e-s for s,e in cuts))
