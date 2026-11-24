/* Small tap feedback for Horoofy Kids: the tapped letter or number pops so a child sees it was heard. */
(()=>{
  const calm=matchMedia('(prefers-reduced-motion:reduce)').matches;
  const pop=el=>{if(!el||calm||!el.animate)return;el.animate([{transform:'scale(1)'},{transform:'scale(1.08)'},{transform:'scale(1)'}],{duration:280})};
  document.addEventListener('click',e=>{
    const c=e.target.closest('.letter-card');
    if(c){const i=c.dataset.index;setTimeout(()=>{const n=document.querySelector(`.letter-card[data-index="${i}"]`);pop(n);n&&n.classList.add('is-heard');setTimeout(()=>n&&n.classList.remove('is-heard'),1500)},40);return}
    pop(e.target.closest('.number-card'));
  });
})();
/* Game answers: green star for a right answer, soft shake for a miss, so feedback is visible and not only text. */
document.addEventListener('click',e=>{
  const b=e.target.closest('.choice');if(!b)return;
  setTimeout(()=>{
    const f=document.querySelector('.game-feedback');
    const ok=f&&f.classList.contains('correct');
    b.classList.add(ok?'is-good':'is-oops');
    if(!ok&&b.animate&&!matchMedia('(prefers-reduced-motion:reduce)').matches)b.animate([{transform:'translateX(0)'},{transform:'translateX(-8px)'},{transform:'translateX(8px)'},{transform:'translateX(0)'}],{duration:260});
    setTimeout(()=>b.classList.remove('is-oops'),700);
  },60);
});
