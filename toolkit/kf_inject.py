import sys
f=sys.argv[1]; h=open(f).read()
js=r'''
 for(const g of document.querySelectorAll('[data-kf]')){
  const K=JSON.parse(g.dataset.kf); const T=K.map(k=>(S[k[0]]??0)+k[1]);
  let x=K[0][2],y=K[0][3],a=K[0][4];
  if(t>=T[T.length-1]){const k=K[K.length-1];x=k[2];y=k[3];a=k[4];}
  else for(let i=0;i<K.length-1;i++){ if(t>=T[i]&&t<T[i+1]){
    const q=T[i+1]-T[i]; let p=q>0?(t-T[i])/q:1; const m=K[i+1][5]||'l';
    if(m==='io') p=p<.5?2*p*p:1-Math.pow(-2*p+2,2)/2; else if(m==='i') p=p*p; else if(m==='o') p=1-(1-p)*(1-p);
    x=K[i][2]+(K[i+1][2]-K[i][2])*p; y=K[i][3]+(K[i+1][3]-K[i][3])*p; a=K[i][4]+(K[i+1][4]-K[i][4])*p; break; } }
  g.setAttribute('transform',`translate(${x} ${y}) rotate(${a})`);
 }
'''
assert " // sketches" in h
h=h.replace(" // sketches", js+" // sketches",1)
open(f,"w").write(h); print("kf ok")
