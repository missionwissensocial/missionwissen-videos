import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
PUR="#7B3FE4"; TQ="#19C6B4"; INK="#0B0B10"
def defs(p):
    return f'''<defs>
<radialGradient id="{p}shell" cx="0.32" cy="0.22" r="0.95"><stop offset="0" stop-color="#FFFFFF"/><stop offset="0.45" stop-color="#EEF0F5"/><stop offset="0.8" stop-color="#CDD2DD"/><stop offset="1" stop-color="#AEB5C3"/></radialGradient>
<linearGradient id="{p}rim" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity="1"/><stop offset="0.5" stop-color="#FFFFFF" stop-opacity="0.25"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>
<linearGradient id="{p}visor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#20202E"/><stop offset="1" stop-color="#07070B"/></linearGradient>
<radialGradient id="{p}shadow"><stop offset="0" stop-color="{INK}" stop-opacity="0.28"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></radialGradient>
<radialGradient id="{p}hover"><stop offset="0" stop-color="{TQ}" stop-opacity="0.4"/><stop offset="1" stop-color="{TQ}" stop-opacity="0"/></radialGradient>
<filter id="{p}glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="3.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="{p}soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="{p}drop" filterUnits="userSpaceOnUse" x="-100" y="-100" width="400" height="480"><feDropShadow dx="0" dy="8" stdDeviation="9" flood-color="#1A1F33" flood-opacity="0.16"/><feDropShadow dx="0" dy="1.5" stdDeviation="1.2" flood-color="#1A1F33" flood-opacity="0.18"/></filter>
</defs>'''
def shape(x,y,w,h,rx,p):
    # soft shaded shell + faint edge + inner top highlight
    return (f'<g filter="url(#{p}drop)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="url(#{p}shell)"/></g>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="none" stroke="#1A1F33" stroke-opacity="0.10" stroke-width="1"/>'
            f'<rect x="{x+1.5}" y="{y+1.5}" width="{w-3}" height="{h-3}" rx="{rx-1.5}" fill="none" stroke="url(#{p}rim)" stroke-width="2"/>')
def eyes(kind,p):
    g=f'fill="{TQ}" filter="url(#{p}glow)"'
    if kind=="happy": return f'<path d="M78 84 q8 -10 16 0 M106 84 q8 -10 16 0" fill="none" stroke="{TQ}" stroke-width="6" stroke-linecap="round" filter="url(#{p}glow)"/>'
    if kind=="think": return f'<rect x="84" y="68" width="11" height="15" rx="5.5" {g}/><rect x="110" y="68" width="11" height="15" rx="5.5" {g}/>'
    if kind=="wow": return f'<circle cx="88" cy="81" r="7.5" {g}/><circle cx="112" cy="81" r="7.5" {g}/>'
    return f'<rect x="81" y="71" width="11" height="18" rx="5.5" {g}/><rect x="108" y="71" width="11" height="18" rx="5.5" {g}/>'
def arm(side,kind,p):
    if side=="l": cx,cy,r = 50,176,(150 if kind=="wave" else 8)
    else: cx,cy,r = 150,176,{"point":-128,"think":-205}.get(kind,-8)
    return f'<g transform="rotate({r} {cx} {cy-20})">{shape(cx-8,cy-22,16,46,8,p)}</g>'
def robot(p, eye="neutral", la="down", ra="down", tilt=0):
    back = "" if ra=="think" else arm("r",ra,p)
    front = arm("r",ra,p) if ra=="think" else ""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="560" viewBox="0 0 200 280">{defs(p)}
<ellipse cx="100" cy="258" rx="44" ry="8" fill="url(#{p}shadow)"/>
<ellipse cx="100" cy="247" rx="28" ry="5" fill="url(#{p}hover)"/>
<g transform="rotate({tilt} 100 150)">{arm("l",la,p)}{back}
{shape(64,134,72,96,36,p)}
<circle cx="100" cy="176" r="12" fill="{TQ}" opacity="0.3" filter="url(#{p}soft)"/>
<circle cx="100" cy="176" r="7" fill="{TQ}"/>
<line x1="100" y1="42" x2="100" y2="22" stroke="#9AA1AE" stroke-width="3" stroke-linecap="round"/>
<circle cx="100" cy="17" r="10" fill="{PUR}" opacity="0.3" filter="url(#{p}soft)"/>
<circle cx="100" cy="17" r="6" fill="{PUR}"/>
{shape(44,40,112,88,40,p)}
<rect x="56" y="54" width="88" height="58" rx="27" fill="url(#{p}visor)"/>
<path d="M66 64 q14 -6 30 -4" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.18"/>
{eyes(eye,p)}
{front}</g></svg>'''
poses={"neutral":dict(),"zeigt":dict(ra="point",tilt=-3),"winkt":dict(eye="happy",la="wave",tilt=3),"denkt":dict(eye="think",ra="think"),"staunt":dict(eye="wow")}
os.makedirs("out",exist_ok=True)
for n,k in poses.items(): open(f"out/robo-{n}.svg","w").write(robot("s"+n[:2]+"-",**k))
