const $ = (id)=>document.getElementById(id);

function esc(s){
  return String(s ?? "")
    .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
    .replace(/"/g,"&quot;").replace(/'/g,"&#039;");
}

function safeUpper(x){ return String(x ?? "").trim().toUpperCase(); }
function safeLower(x){ return String(x ?? "").trim().toLowerCase(); }
function rupees(n){ return "₹" + Math.round(Number(n)||0).toLocaleString("en-IN"); }

function splitCSV(s){
  return String(s||"")
    .split(",")
    .map(x=>x.trim())
    .filter(Boolean);
}

/* ========= District content data ========= */
const DISTRICTS = {
  bilaspur: { name:"Bilaspur", hero:"./style/bilaspur.jpg", hq:"Bilaspur", region:"Shivalik / Lower Himalayas",
    knownFor:["Gobind Sagar","Bhakra–Nangal region","Lakeside viewpoints"],
    about:["Bilaspur is known for reservoir landscapes around Gobind Sagar and its gateway positioning within Himachal Pradesh.","Use travel writing tone (Balokhra-inspired) but keep facts consistent with Wikipedia."],
    attractions:["Gobind Sagar Lake","Bhakra Dam vicinity","Local temples & viewpoints"],
    bestTime:["Oct–Mar","Apr–Jun"],
    wiki:"https://en.wikipedia.org/wiki/Bilaspur_district,_Himachal_Pradesh"
  },
  chamba: { name:"Chamba", hero:"./style/chamba.jpg", hq:"Chamba", region:"Western Himalayas",
    knownFor:["Ravi valley","Chamba culture","Temples & heritage"],
    about:["Chamba district is known for mountainous landscapes, strong cultural identity and historic temples.","Use Balokhra-style storytelling; verify admin facts on Wikipedia."],
    attractions:["Chamba heritage areas","Temples","Mountain valleys & viewpoints"],
    bestTime:["Mar–Jun","Sep–Nov"],
    wiki:"https://en.wikipedia.org/wiki/Chamba_district"
  },
  hamirpur: { name:"Hamirpur", hero:"./style/hamirpur.jpg", hq:"Hamirpur", region:"Lower Himalayas / Foothills",
    knownFor:["Education hub","Central location","Easy road access"],
    about:["Hamirpur is often described as well-connected with a strong education-focused identity.","Use tourism tone; keep factual anchors aligned with Wikipedia."],
    attractions:["Local temples","Town markets","Scenic hill drives"],
    bestTime:["Oct–Mar","Apr–Jun"],
    wiki:"https://en.wikipedia.org/wiki/Hamirpur_district,_Himachal_Pradesh"
  },
  kangra: { name:"Kangra", hero:"./style/kangra.jpg", hq:"Dharamshala", region:"Dhauladhar / Kangra Valley",
    knownFor:["Dharamshala–McLeod Ganj","Kangra Valley","Forts & temples"],
    about:["Kangra includes the Kangra Valley and Dhauladhar backdrop; Dharamshala is the HQ and a major tourism magnet.","Blend Balokhra-style narrative with Wikipedia-aligned facts."],
    attractions:["Dharamshala & McLeod Ganj","Kangra region","Tea gardens"],
    bestTime:["Mar–Jun","Sep–Nov"],
    wiki:"https://en.wikipedia.org/wiki/Kangra_district"
  },
  kinnaur: { name:"Kinnaur", hero:"./style/kinnaur.jpg", hq:"Reckong Peo", region:"Trans-Himalayan / Sutlej valley",
    knownFor:["High valleys","Apple belt","Kinnauri culture"],
    about:["Kinnaur is a high-altitude district linked with the Sutlej valley, dramatic scenery, and distinct cultural traditions.","Keep facts aligned with Wikipedia; write in your own words."],
    attractions:["Sutlej valley viewpoints","High mountain villages","Orchards (seasonal)"],
    bestTime:["Apr–Jun","Sep–Oct"],
    wiki:"https://en.wikipedia.org/wiki/Kinnaur_district"
  },
  kullu: { name:"Kullu", hero:"./style/kullu.jpg", hq:"Kullu", region:"Beas valley",
    knownFor:["Kullu Valley","Adventure sports","Gateway to Manali"],
    about:["Kullu spans the Beas valley and is known for scenic landscapes and access to Manali-side circuits.","Tourism-style writeup; verify facts using Wikipedia."],
    attractions:["Kullu Valley","Beas riverside spots","Adventure activities (seasonal)"],
    bestTime:["Mar–Jun","Sep–Nov","Dec–Feb (snow nearby)"],
    wiki:"https://en.wikipedia.org/wiki/Kullu_district"
  },
  lahaul_spiti: { name:"Lahaul & Spiti", hero:"./style/lahaul-spiti.jpg", hq:"Keylong", region:"Cold desert / Trans-Himalayan",
    knownFor:["High passes","Monasteries","Cold desert landscapes"],
    about:["Lahaul & Spiti is a high-altitude district known for cold-desert terrain and dramatic passes.","Use narrative tone; keep geography facts aligned with Wikipedia."],
    attractions:["Keylong region","High-altitude viewpoints","Monastery circuits (as applicable)"],
    bestTime:["Jun–Sep","May/Oct (weather dependent)"],
    wiki:"https://en.wikipedia.org/wiki/Lahaul_and_Spiti_district"
  },
  mandi: { name:"Mandi", hero:"./style/mandi.jpg", hq:"Mandi", region:"Central Himachal / River valleys",
    knownFor:["Temple town reputation","Central connectivity","Valley scenery"],
    about:["Mandi is centrally placed with a strong temple-town identity and scenic valley drives.","Use Wikipedia for facts and Balokhra for descriptive tone."],
    attractions:["Temple clusters","Valley drives","Local heritage areas"],
    bestTime:["Oct–Mar","Apr–Jun"],
    wiki:"https://en.wikipedia.org/wiki/Mandi_district"
  },
  shimla: { name:"Shimla", hero:"./style/shimla.jpg", hq:"Shimla", region:"Middle Himalayas",
    knownFor:["State capital region","Heritage-era townscapes","Hill circuits"],
    about:["Shimla district includes the state-capital region and a major tourism belt with heritage townscapes.","Keep official facts aligned with Wikipedia; use a travelogue tone."],
    attractions:["Heritage town areas","Hill viewpoints","Seasonal nature walks"],
    bestTime:["Mar–Jun","Oct–Dec"],
    wiki:"https://en.wikipedia.org/wiki/Shimla_district"
  },
  sirmaur: { name:"Sirmaur", hero:"./style/sirmaur.jpg", hq:"Nahan", region:"Southern Himachal / Shivalik",
    knownFor:["Forested hills","Nahan region","Lower Himachal circuits"],
    about:["Sirmaur lies in southern Himachal and includes Shivalik hill landscapes; Nahan is the HQ.","Use tourism tone; verify facts on Wikipedia."],
    attractions:["Nahan & surroundings","Forested hill spots","Local temples"],
    bestTime:["Oct–Mar","Apr–Jun"],
    wiki:"https://en.wikipedia.org/wiki/Sirmaur_district"
  },
  solan: { name:"Solan", hero:"./style/solan.jpg", hq:"Solan", region:"Lower Himalayas / Shivalik",
    knownFor:["Short trips","Hill-town weather","Gateway from Chandigarh side"],
    about:["Solan is a popular short-trip stay belt in lower Himachal with easy connectivity.","Use Wikipedia facts + your own tourism narration."],
    attractions:["Hill viewpoints","Local temples","Short-drive picnic spots"],
    bestTime:["Mar–Jun","Oct–Dec"],
    wiki:"https://en.wikipedia.org/wiki/Solan_district"
  },
  una: { name:"Una", hero:"./style/una.jpg", hq:"Una", region:"Foothills / Lower Himachal",
    knownFor:["Gateway district","Plains-to-hills transition","Pilgrimage circuits nearby"],
    about:["Una is often treated as a gateway belt connecting plains routes with Himachal hill circuits.","Use tourism tone, keep facts aligned with Wikipedia."],
    attractions:["Temple visits (regional)","Foothill drives","Local markets"],
    bestTime:["Oct–Mar","Apr–Jun"],
    wiki:"https://en.wikipedia.org/wiki/Una_district"
  }
};

function renderDistrict(id){
  const d = DISTRICTS[id];
  if(!d){
    $("dName").textContent = "District not found";
    $("about").innerHTML = `<p class="p">Invalid district key: <b>${esc(id)}</b></p>`;
    return;
  }

  document.title = `${d.name} | Himachal Explorer District Guide`;

  $("dName").textContent = d.name;
  $("dSub").textContent = `District Guide • Facts • Places • Routes`;
  $("heroImg").src = d.hero;

  $("factHQ").textContent = d.hq || "—";
  $("factRegion").textContent = d.region || "—";
  $("factWiki").innerHTML = d.wiki ? `<a href="${esc(d.wiki)}" target="_blank" rel="noopener">Open Wikipedia</a>` : "—";
  $("factBest").textContent = (d.bestTime || []).join(" • ") || "—";

  $("about").innerHTML = (d.about || []).map(t=>`<p class="p">${esc(t)}</p>`).join("");

  $("knownFor").innerHTML = (d.knownFor || []).map(x=>`<span class="tag">${esc(x)}</span>`).join("");
  $("attractions").innerHTML = (d.attractions || []).map(x=>`<span class="tag">${esc(x)}</span>`).join("");

  // expose current district name for package filtering
  window.__DISTRICT_NAME__ = safeUpper(d.name);
}

/* ========= Firebase packages section ========= */

/* Change if your dashboard file name is different */
const DASHBOARD_URL = "./dashboard.html";

/* You can keep these in your style folder */
const FALLBACK_IMG = "./style/n1.jpg";

/* Same helper logic as your dashboard to pick image */
function pickPackageCover(tpl){
  const maybe = [tpl.cover, tpl.photo, tpl.image].map(x=>String(x||"").trim()).filter(Boolean);
  if(maybe.length) return maybe[0];

  // Try day1 / day2 place IDs based naming, optional
  const d1 = splitCSV(tpl.day1_place_ids || "");
  const pid = d1[0] || "";
  if(pid) return `./Places/${pid}_1.jpg`;
  return FALLBACK_IMG;
}

function pickTitle(tpl, key){
  return String(tpl.package_name || tpl.route_name || key || "PACKAGE").trim();
}

function pickStart(tpl){
  return safeUpper(tpl.start_point || tpl.start || "");
}

function pickDays(tpl){
  const d = Number(tpl.days || 0);
  return d ? d : "";
}

function pickPriceAny(tpl){
  // fallback from template (since district pages don’t load cost node)
  const b = Number(tpl.budget_price_per_person || tpl.budget_price || 0);
  const p = Number(tpl.premium_price_per_person || tpl.premium_price || 0);
  const l = Number(tpl.luxury_price_per_person || tpl.luxury_price || 0);
  return b || p || l || 0;
}

function buildDashboardLink({ districtName, start, days, tier="budget", pax="2" }){
  const u = new URL(DASHBOARD_URL, location.href);
  u.searchParams.set("origin","in");
  u.searchParams.set("district", districtName);
  if(start) u.searchParams.set("start", start);
  if(days) u.searchParams.set("days", String(days));
  u.searchParams.set("tier", tier);
  u.searchParams.set("pax", pax);
  return u.toString();
}

/* renders tiles into #districtPackages */
function renderDistrictPackages(templatesObj, districtName){
  const host = $("districtPackages");
  if(!host) return;

  const list = Object.entries(templatesObj || {}).map(([k,v])=>({ key:k, ...(v||{}) }));

  const filtered = list
    .filter(t => safeUpper(t.district || "") === districtName)
    .sort((a,b)=> (Number(a.days||0)-Number(b.days||0)) || pickTitle(a,a.key).localeCompare(pickTitle(b,b.key)));

  if(!filtered.length){
    host.innerHTML = `<p class="p">No packages found for <b>${esc(districtName)}</b> in Firebase <code>templates</code>.</p>`;
    return;
  }

  const tier = "budget";
  const pax = "2";

  host.innerHTML = `
    <div style="display:flex; gap:10px; overflow:auto; padding-bottom:2px; -webkit-overflow-scrolling:touch;">
      ${filtered.slice(0, 24).map(t=>{
        const title = pickTitle(t, t.key);
        const cover = pickPackageCover(t);
        const start = pickStart(t);
        const days = pickDays(t);
        const price = pickPriceAny(t);
        const link = buildDashboardLink({ districtName, start, days, tier, pax });

        return `
          <a href="${esc(link)}" style="
            text-decoration:none; color:inherit;
            flex:0 0 auto; width: 220px;
            border:1px solid rgba(10,30,60,.14);
            background: rgba(255,255,255,.72);
            border-radius: 16px;
            box-shadow: 0 10px 20px rgba(10,30,60,.08);
            overflow:hidden;
            display:block;
          ">
            <div style="height:120px; border-bottom:1px solid rgba(10,30,60,.12); background: rgba(255,255,255,.66);">
              <img src="${esc(cover)}" onerror="this.src='${esc(FALLBACK_IMG)}'"
                   style="width:100%; height:100%; object-fit:cover; display:block;">
            </div>
            <div style="padding:10px;">
              <div style="font-size:10.5px; font-weight:1200; letter-spacing:.12em; text-transform:uppercase; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                ${esc(title)}
              </div>
              <div style="margin-top:6px; font-size:9.5px; letter-spacing:.10em; text-transform:uppercase; color: rgba(10,30,60,.62); display:flex; gap:6px; flex-wrap:wrap;">
                ${days ? `<span style="border:1px solid rgba(10,30,60,.12); background: rgba(255,255,255,.66); border-radius:999px; padding:5px 7px;">${esc(days)}D</span>` : ""}
                ${start ? `<span style="border:1px solid rgba(10,30,60,.12); background: rgba(255,255,255,.66); border-radius:999px; padding:5px 7px;">${esc(start)}</span>` : ""}
              </div>
              <div style="margin-top:8px; font-size:10px; letter-spacing:.10em; text-transform:uppercase; color: rgba(10,30,60,.66);">
                Starting <b style="display:block; margin-top:2px; font-size:12px; letter-spacing:.06em; color: rgba(10,30,60,.92);">
                  ${price ? esc(rupees(price)) : "—"} / person
                </b>
              </div>
            </div>
          </a>
        `;
      }).join("")}
    </div>
    <div style="margin-top:10px; font-size:11px; color: rgba(10,30,60,.72); line-height:1.45;">
      Tap any package to open the Dashboard filtered for <b>${esc(districtName)}</b>.
    </div>
  `;
}

/* ===== Public APIs ===== */
window.renderDistrict = renderDistrict;
window.renderDistrictPackages = renderDistrictPackages;
