const toggle = document.querySelector('.menu-toggle');
const menu = document.querySelector('#mobile-menu');
function closeMenu(restoreFocus = false) {
  if (!toggle || !menu) return;
  menu.hidden = true;
  toggle.setAttribute('aria-expanded', 'false');
  toggle.setAttribute('aria-label', 'Open menu');
  document.body.style.overflow = '';
  if (restoreFocus) toggle.focus();
}
if (toggle && menu) {
  toggle.addEventListener('click', () => {
    const opening = menu.hidden;
    menu.hidden = !opening;
    toggle.setAttribute('aria-expanded', String(opening));
    toggle.setAttribute('aria-label', opening ? 'Close menu' : 'Open menu');
    document.body.style.overflow = opening ? 'hidden' : '';
    if (opening) menu.querySelector('a').focus();
  });
  menu.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
    closeMenu();
    const target = document.querySelector(link.hash);
    if (target) { target.tabIndex = -1; target.focus({preventScroll:true}); }
  }));
  document.addEventListener('keydown', event => {
    if (menu.hidden) return;
    if (event.key === 'Escape') closeMenu(true);
    if (event.key === 'Tab') {
      const items = [toggle, ...menu.querySelectorAll('a')];
      const first = items[0], last = items.at(-1);
      if (event.shiftKey && document.activeElement === first) {event.preventDefault(); last.focus();}
      else if (!event.shiftKey && document.activeElement === last) {event.preventDefault(); first.focus();}
    }
  });
  matchMedia('(min-width: 761px)').addEventListener('change', event => { if(event.matches) closeMenu(); });
}
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
if ('IntersectionObserver' in window) {
  const currentNav = new IntersectionObserver(entries => {
    for (const entry of entries) {
      const link = document.querySelector(`.site-header nav a[href="#${entry.target.id}"]`);
      if (link) { if(entry.isIntersecting) link.setAttribute('aria-current', 'location'); else link.removeAttribute('aria-current'); }
    }
  }, {rootMargin:'-15% 0px -55% 0px'});
  document.querySelectorAll('#features,#journal,#faq').forEach(section=>currentNav.observe(section));
  if (!reducedMotion.matches) {
    const reveals = new IntersectionObserver(entries=>entries.forEach(entry=>{
      if(entry.isIntersecting){entry.target.classList.add('visible');reveals.unobserve(entry.target);}
    }),{threshold:.06});
    document.querySelectorAll('.benefit-grid,.walkthrough,.journal-card').forEach(section=>{
      section.classList.add('reveal-ready'); reveals.observe(section);
    });
    // Inline words cross a viewport trigger in reading order; each activates once.
    const tagline = document.querySelector('.tagline');
    if(tagline){
      let index=0;
      [...tagline.childNodes].forEach(node=>{
        if(node.nodeType!==Node.TEXT_NODE)return;
        const fragment=document.createDocumentFragment();
        node.textContent.split(/(\s+)/).forEach(word=>{
          if(!word.trim())fragment.append(word);
          else {const span=document.createElement('span');span.className='tagline-word';span.textContent=word;span.style.transitionDelay=`${(index++ % 6)*60}ms`;fragment.append(span);}
        });
        node.replaceWith(fragment);
      });
      const words=new IntersectionObserver(entries=>entries.forEach(entry=>{
        if(entry.isIntersecting){entry.target.classList.add('lit');words.unobserve(entry.target);}
      }),{rootMargin:'0px 0px -18% 0px',threshold:1});
      tagline.querySelectorAll('.tagline-word').forEach(word=>words.observe(word));
    }
  }
}
// No external analytics, cookies, user identifiers, or tracking requests.
