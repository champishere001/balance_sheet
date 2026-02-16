<script>
window.UI = {
  qs(sel, root=document){ return root.querySelector(sel); },
  qsa(sel, root=document){ return [...root.querySelectorAll(sel)]; },
  fmtINR(n){
    try { return new Intl.NumberFormat("en-IN",{style:"currency",currency:"INR",maximumFractionDigits:0}).format(n); }
    catch(e){ return "₹"+Math.round(n); }
  },
  getParam(key){
    const u = new URL(location.href);
    return u.searchParams.get(key);
  },
  setActiveNav(){
    const file = location.pathname.split("/").pop() || "index.html";
    UI.qsa(".nav a").forEach(a=>{
      const href = a.getAttribute("href");
      if(href === file) a.classList.add("active");
    });
  },
  openModal(id){ UI.qs(id).classList.remove("hidden"); },
  closeModal(id){ UI.qs(id).classList.add("hidden"); },
  firstVisitModal(){
    const key="hpPortal_seen";
    if(!localStorage.getItem(key)){
      UI.openModal("#capModal");
      localStorage.setItem(key,"1");
    }
  }
};
</script>
