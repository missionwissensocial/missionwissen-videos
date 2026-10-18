# splice.py TEMPLATE BEATS_SCENES OUT : replaces CH/B block and scene block of the Winterreifen build
import sys
tpl=open(sys.argv[1]).read(); part=open(sys.argv[2]).read()
beats_part, scenes_part = part.split("#===SCENES===\n")
a=tpl.index("CH = ["); b=tpl.index("# word start times")
tpl=tpl[:a]+beats_part+tpl[b:]
a=tpl.index("# ---------- sketches ----------"); b=tpl.index("# ---- End card")
tpl=tpl[:a]+scenes_part+"\n"+tpl[b:]
open(sys.argv[3],"w").write(tpl)
