(()=>{
 const section=document.getElementById('sources');if(!section)return;
 const buttons=[...section.querySelectorAll('[data-source]')];
 const panels=[...section.querySelectorAll('.ds-panel')];
 for(const button of buttons)button.addEventListener('click',()=>{
  const open=button.getAttribute('aria-expanded')!=='true';
  for(const other of buttons)other.setAttribute('aria-expanded',String(other===button&&open));
  for(const panel of panels)panel.hidden=!(open&&panel.id===button.getAttribute('aria-controls'));
 });
 function language(){section.dataset.lang=document.querySelector('.dp-lang').textContent==='EN'?'el':'en';}
 document.querySelector('.dp-lang').addEventListener('click',language);language();
})();
