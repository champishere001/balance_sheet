<script>
window.App = {
  state:{
    district:"all",
    type:"all",
    q:"",
  },

  initCommon(){
    UI.setActiveNav();
    // Fill district dropdowns
    UI.qsa("[data-fill='districts']").forEach(sel=>{
      sel.innerHTML = `<option value="all">All Districts</option>` + 
        HP_DATA.districts.map(d=>`<option value="${d.id}">${d.name}</option>`).join("");
    });

    // Fill quick district pills
    const pillWrap = UI.qs("#districtPills");
    if(pillWrap){
      pillWrap.innerHTML = `<div class="pill ${App.state.district==='all'?'active':''}" data-d="all">All</div>` +
        HP_DATA.districts.map(d=>`<div class="pill" data-d="${d.id}">${d.name}</div>`).join("");
      pillWrap.addEventListener("click",(e)=>{
        const p = e.target.closest(".pill"); if(!p) return;
        App.setDistrict(p.dataset.d);
      });
    }

    // First visit popup
    if(UI.qs("#capModal")) UI.firstVisitModal();

    // Close modal handlers
    UI.qsa("[data-close]").forEach(btn=>{
      btn.addEventListener("click",()=>UI.closeModal(btn.dataset.close));
    });
  },

  setDistrict(d){
    App.state.district = d || "all";
    // update dropdown
    const dd = UI.qs("#districtSelect");
    if(dd) dd.value = App.state.district;
    // update pills
    UI.qsa("#districtPills .pill").forEach(p=>{
      p.classList.toggle("active", p.dataset.d === App.state.district);
    });
    App.renderCards();
  },

  setType(t){
    App.state.type = t || "all";
    const typePills = UI.qsa("#typePills .pill");
    typePills.forEach(p=>p.classList.toggle("active", p.dataset.t === App.state.type));
    App.renderCards();
  },

  setQuery(q){
    App.state.q = (q||"").trim().toLowerCase();
    App.renderCards();
  },

  filterItems(){
    return HP_DATA.items.filter(x=>{
      const okDistrict = (App.state.district==="all") || (x.district===App.state.district);
      const okType = (App.state.type==="all") || (x.type===App.state.type);
      const okQ = !App.state.q || (
        x.name.toLowerCase().includes(App.state.q) ||
        (x.short||"").toLowerCase().includes(App.state.q) ||
        (x.tags||[]).join(" ").toLowerCase().includes(App.state.q)
      );
      return okDistrict && okType && okQ;
    });
  },

  cardLink(item){
    // Places go to place.html, others go to their listing pages filtered
    if(item.type==="place") return `place.html?id=${encodeURIComponent(item.id)}`;
    if(item.type==="hotel") return `hotels.html?district=${encodeURIComponent(item.district)}`;
    if(item.type==="temple") return `temples.html?district=${encodeURIComponent(item.district)}`;
    if(item.type==="trek") return `treks.html?district=${encodeURIComponent(item.district)}`;
    return "#";
  },

  renderCards(targetId="cardsWrap", metaId="cardsMeta"){
    const wrap = UI.qs("#"+targetId);
    if(!wrap) return;

    const items = App.filterItems();
    const meta = UI.qs("#"+metaId);
    if(meta) meta.textContent = `${items.length} results`;

    wrap.innerHTML = items.map(item=>{
      const distName = HP_DATA.districts.find(d=>d.id===item.district)?.name || item.district;
      const icons = {
        place:"📍 Place",
        hotel:"🏨 Hotel",
        temple:"🛕 Temple",
        trek:"🥾 Trek"
      };
      const extra = item.type==="hotel" && item.priceFrom ? `<div class="iconChip">From ${UI.fmtINR(item.priceFrom)}</div>` : "";
      const diff = item.type==="trek" && item.difficulty ? `<div class="iconChip">${item.difficulty}</div>` : "";
      return `
      <a class="card" href="${App.cardLink(item)}">
        <div class="img">
          <img src="${item.img}" alt="${item.name}">
          <div class="badges">
            <div class="badge">${distName}</div>
            <div class="badge">${icons[item.type] || "Info"}</div>
          </div>
        </div>
        <div class="body">
          <div class="titleRow">
            <h3>${item.name}</h3>
          </div>
          <p>${item.short || ""}</p>
          <div class="quickIcons">
            ${(item.tags||[]).slice(0,3).map(t=>`<div class="iconChip">${t}</div>`).join("")}
            ${extra}${diff}
          </div>
        </div>
      </a>`;
    }).join("");
  },

  initHome(){
    App.initCommon();

    // Sidebar type pills
    const typeWrap = UI.qs("#typePills");
    if(typeWrap){
      typeWrap.innerHTML = `
        <div class="pill active" data-t="all">All</div>
        <div class="pill" data-t="place">Places</div>
        <div class="pill" data-t="hotel">Hotels</div>
        <div class="pill" data-t="temple">Temples</div>
        <div class="pill" data-t="trek">Treks</div>
      `;
      typeWrap.addEventListener("click",(e)=>{
        const p = e.target.closest(".pill"); if(!p) return;
        App.setType(p.dataset.t);
      });
    }

    // Controls
    const dd = UI.qs("#districtSelect");
    if(dd){
      dd.addEventListener("change", ()=>App.setDistrict(dd.value));
    }
    const q = UI.qs("#searchInput");
    if(q){
      q.addEventListener("input", ()=>App.setQuery(q.value));
    }

    // Hero controls
    const heroDistrict = UI.qs("#heroDistrict");
    const heroCategory = UI.qs("#heroCategory");
    const heroQuery = UI.qs("#heroQuery");
    const heroGo = UI.qs("#heroGo");
    if(heroGo){
      heroGo.addEventListener("click", ()=>{
        App.setDistrict(heroDistrict?.value || "all");
        App.setType(heroCategory?.value || "all");
        App.setQuery(heroQuery?.value || "");
        window.scrollTo({top: 520, behavior:"smooth"});
      });
    }

    App.renderCards();
  },

  initListing(listType){ // hotels/temples/treks/places (districts page uses its own)
    App.initCommon();
    // seed from URL
    const d = UI.getParam("district");
    if(d) App.state.district = d;
    App.state.type = listType;

    const dd = UI.qs("#districtSelect");
    if(dd){
      dd.value = App.state.district || "all";
      dd.addEventListener("change", ()=>App.setDistrict(dd.value));
    }
    const q = UI.qs("#searchInput");
    if(q) q.addEventListener("input", ()=>App.setQuery(q.value));

    // fixed type
    App.renderCards();
  },

  initDistricts(){
    App.initCommon();
    const wrap = UI.qs("#districtGrid");
    wrap.innerHTML = HP_DATA.districts.map(d=>{
      const heroImg = {
        shimla:"https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=1600&q=70",
        kullu:"https://images.unsplash.com/photo-1627920769842-6887c6df05ca?auto=format&fit=crop&w=1600&q=70",
        kangra:"https://images.unsplash.com/photo-1626497764746-6dc36546b388?auto=format&fit=crop&w=1600&q=70",
        mandi:"https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1600&q=70",
        chamba:"https://images.unsplash.com/photo-1482192596544-9eb780fc7f66?auto=format&fit=crop&w=1600&q=70",
      }[d.id] || "https://images.unsplash.com/photo-1482192596544-9eb780fc7f66?auto=format&fit=crop&w=1600&q=70";

      return `
        <a class="card" href="index.html?district=${encodeURIComponent(d.id)}">
          <div class="img"><img src="${heroImg}" alt="${d.name}">
            <div class="badges"><div class="badge">District</div></div>
          </div>
          <div class="body">
            <h3>${d.name}</h3>
            <p>Explore places, hotels, temples & treks in ${d.name}.</p>
            <div class="quickIcons">
              <div class="iconChip">Places</div>
              <div class="iconChip">Hotels</div>
              <div class="iconChip">Routes</div>
            </div>
          </div>
        </a>`;
    }).join("");
  },

  initPlace(){
    App.initCommon();
    const id = UI.getParam("id");
    const item = HP_DATA.items.find(x=>x.id===id && x.type==="place");
    if(!item){
      UI.qs("#placeWrap").innerHTML = `<div class="panel"><h3>Place not found</h3><div class="note">Go back to <a href="index.html">Home</a></div></div>`;
      return;
    }
    const distName = HP_DATA.districts.find(d=>d.id===item.district)?.name || item.district;

    // render header
    UI.qs("#placeHeroImg").src = item.img;
    UI.qs("#placeTitle").textContent = item.name;
    UI.qs("#placeSub").textContent = `${distName} • ${item.tags?.slice(0,3).join(" • ")}`;

    // info panel
    UI.qs("#bestTime").textContent = item.bestTime || "-";
    UI.qs("#highlights").innerHTML = (item.highlights||[]).map(x=>`<div class="iconChip">${x}</div>`).join("");
    UI.qs("#nearby").innerHTML = (item.nearby||[]).map(x=>`<div class="iconChip">${x}</div>`).join("");
    UI.qs("#placeDesc").textContent = item.short || "";

    // Tabs content
    function related(type){
      return HP_DATA.items.filter(x=>x.type===type && x.district===item.district);
    }
    function renderRelated(type){
      const list = related(type);
      const wrap = UI.qs("#tabContent");
      if(list.length===0){
        wrap.innerHTML = `<div class="panel"><h3>No ${type}s added yet</h3><div class="note">Add more in <b>assets/data.js</b></div></div>`;
        return;
      }
      wrap.innerHTML = `<div class="cards">${
        list.map(x=>`
          <a class="card" href="${x.type==='hotel'?'hotels.html':'#'}?district=${encodeURIComponent(x.district)}">
            <div class="img"><img src="${x.img}" alt="${x.name}">
              <div class="badges"><div class="badge">${type.toUpperCase()}</div></div>
            </div>
            <div class="body">
              <h3>${x.name}</h3>
              <p>${x.short || ""}</p>
              <div class="quickIcons">
                ${(x.tags||[]).slice(0,3).map(t=>`<div class="iconChip">${t}</div>`).join("")}
                ${(x.priceFrom?`<div class="iconChip">From ${UI.fmtINR(x.priceFrom)}</div>`:"")}
                ${(x.difficulty?`<div class="iconChip">${x.difficulty}</div>`:"")}
              </div>
            </div>
          </a>
        `).join("")
      }</div>`;
    }

    // Tabs
    const tabs = UI.qsa(".tab");
    const setTab = (t)=>{
      tabs.forEach(x=>x.classList.toggle("active", x.dataset.tab===t));
      if(t==="hotels") renderRelated("hotel");
      if(t==="temples") renderRelated("temple");
      if(t==="treks") renderRelated("trek");
      if(t==="gallery"){
        UI.qs("#tabContent").innerHTML = `
          <div class="cards">
            ${[item.img,
              "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1600&q=70",
              "https://images.unsplash.com/photo-1526481280695-3c687fd5432c?auto=format&fit=crop&w=1600&q=70"
            ].map(u=>`
              <div class="card">
                <div class="img"><img src="${u}" alt="Gallery"></div>
                <div class="body"><p>Photo preview (replace with your real photos later).</p></div>
              </div>
            `).join("")}
          </div>`;
      }
    };
    tabs.forEach(t=>t.addEventListener("click", ()=>setTab(t.dataset.tab)));
    setTab("hotels");

    // Route + expenditure calculator (demo)
    const fuel = UI.qs("#fuelCost");
    const kmpl = UI.qs("#kmpl");
    const toll = UI.qs("#toll");
    const days = UI.qs("#days");
    const perDay = UI.qs("#perDay");
    const calcBtn = UI.qs("#calcBtn");
    const out = UI.qs("#calcOut");

    // approximate km (demo) from matrix or fallback
    const baseKey = `${item.district}:${item.id}`;
    const approxKm = HP_DATA.distances_km[baseKey] || 35;

    UI.qs("#approxKm").textContent = `${approxKm} km (approx.)`;

    calcBtn.addEventListener("click", ()=>{
      const fuelCost = Number(fuel.value||0);
      const kmPerL = Math.max(1, Number(kmpl.value||12));
      const tollCost = Number(toll.value||0);
      const numDays = Math.max(1, Number(days.value||1));
      const perDayCost = Number(perDay.value||0);

      const fuelLiters = approxKm / kmPerL;
      const fuelTotal = fuelLiters * fuelCost;
      const stayFood = numDays * perDayCost;
      const total = fuelTotal + tollCost + stayFood;

      out.innerHTML = `
        <div class="kv">
          <div class="item"><b>Distance</b><span>${approxKm} km</span></div>
          <div class="item"><b>Fuel (approx.)</b><span>${UI.fmtINR(fuelTotal)}</span></div>
          <div class="item"><b>Toll/Parking</b><span>${UI.fmtINR(tollCost)}</span></div>
          <div class="item"><b>Stay+Food</b><span>${UI.fmtINR(stayFood)}</span></div>
        </div>
        <div class="divider"></div>
        <div class="item" style="border:1px solid rgba(103,232,249,.35); background:rgba(103,232,249,.08); border-radius:16px; padding:12px;">
          <b style="color:var(--muted); display:block; font-size:12px;">Estimated Total</b>
          <span style="font-size:18px; font-weight:900;">${UI.fmtINR(total)}</span>
          <div class="note" style="margin-top:6px;">Demo calculator. Replace km with real Google Maps distance later.</div>
        </div>
      `;
    });
  }
};
</script>
