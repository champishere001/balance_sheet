const $ = (id)=>document.getElementById(id);

function esc(s){
  return String(s ?? "")
    .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
    .replace(/"/g,"&quot;").replace(/'/g,"&#039;");
}

const DISTRICTS = {
  bilaspur: {
    name: "Bilaspur",
    hero: "./style/bilaspur.jpg",
    hq: "Bilaspur",
    region: "Shivalik / Lower Himalayas",
    knownFor: ["Gobind Sagar", "Bhakra–Nangal region", "Lakeside viewpoints"],
    about: [
      "Bilaspur is known for its reservoir landscapes around Gobind Sagar and its role as an important gateway district in Himachal Pradesh.",
      "For a tourism-style narrative, you can align this page with descriptions from Jagmohan Balokhra’s ‘The Wonderland of Himachal Pradesh’ while keeping factual points consistent with Wikipedia."
    ],
    attractions: ["Gobind Sagar Lake", "Bhakra Dam vicinity", "Local temples & viewpoints"],
    bestTime: ["Oct–Mar (pleasant)", "Apr–Jun (warm; lake views)"],
    wiki: "https://en.wikipedia.org/wiki/Bilaspur_district,_Himachal_Pradesh"
  },

  chamba: {
    name: "Chamba",
    hero: "./style/chamba.jpg",
    hq: "Chamba",
    region: "Western Himalayas",
    knownFor: ["Ravi valley", "Chamba culture", "Temples & heritage"],
    about: [
      "Chamba district is known for its mountainous landscapes, strong cultural identity and historic temples, with the Ravi river system shaping many valleys.",
      "Use Balokhra’s ‘Wonderland’ as a descriptive reference; keep core facts aligned with Wikipedia."
    ],
    attractions: ["Chamba town heritage", "Temples", "Mountain valleys & viewpoints"],
    bestTime: ["Mar–Jun", "Sep–Nov"],
    wiki: "https://en.wikipedia.org/wiki/Chamba_district"
  },

  hamirpur: {
    name: "Hamirpur",
    hero: "./style/hamirpur.jpg",
    hq: "Hamirpur",
    region: "Lower Himalayas / Foothills",
    knownFor: ["Education hub", "Central location", "Easy road access"],
    about: [
      "Hamirpur is among Himachal’s smaller districts by area and is often described as well-connected with a strong education-focused identity.",
      "Use Balokhra’s narrative tone for tourism writing; verify administrative facts on Wikipedia."
    ],
    attractions: ["Local temples", "Town markets", "Scenic hill drives"],
    bestTime: ["Oct–Mar", "Apr–Jun"],
    wiki: "https://en.wikipedia.org/wiki/Hamirpur_district,_Himachal_Pradesh"
  },

  kangra: {
    name: "Kangra",
    hero: "./style/kangra.jpg",
    hq: "Dharamshala",
    region: "Dhauladhar range / Kangra Valley",
    knownFor: ["Dharamshala–McLeod Ganj", "Kangra Valley", "Heritage forts & temples"],
    about: [
      "Kangra district includes the Kangra Valley and the Dhauladhar mountain backdrop; Dharamshala is the district headquarters and a major tourism magnet.",
      "Blend Balokhra-style storytelling with Wikipedia-aligned facts for clean, reliable content."
    ],
    attractions: ["Dharamshala & McLeod Ganj", "Kangra Fort region", "Tea gardens"],
    bestTime: ["Mar–Jun", "Sep–Nov"],
    wiki: "https://en.wikipedia.org/wiki/Kangra_district"
  },

  kinnaur: {
    name: "Kinnaur",
    hero: "./style/kinnaur.jpg",
    hq: "Reckong Peo",
    region: "Trans-Himalayan / Sutlej valley",
    knownFor: ["High-altitude valleys", "Apple belt", "Kinnauri culture"],
    about: [
      "Kinnaur is a high-altitude district associated with the Sutlej valley, dramatic mountain scenery, and distinct Kinnauri cultural traditions.",
      "If you quote or paraphrase ‘Wonderland’, keep it short and rewrite in your own words; use Wikipedia for factual anchors."
    ],
    attractions: ["Sutlej valley viewpoints", "High mountain villages", "Orchards (seasonal)"],
    bestTime: ["Apr–Jun", "Sep–Oct"],
    wiki: "https://en.wikipedia.org/wiki/Kinnaur_district"
  },

  kullu: {
    name: "Kullu",
    hero: "./style/kullu.jpg",
    hq: "Kullu",
    region: "Beas valley",
    knownFor: ["Kullu Valley", "Adventure sports", "Gateway to Manali"],
    about: [
      "Kullu district spans the Beas valley and is widely known for its scenic valley landscapes and access toward Manali-side tourism circuits.",
      "This page is written in a tourism format; verify factual points from Wikipedia and use Balokhra as a descriptive reference."
    ],
    attractions: ["Kullu Valley", "Beas riverside spots", "Adventure activities (seasonal)"],
    bestTime: ["Mar–Jun", "Sep–Nov", "Dec–Feb (snow nearby)"],
    wiki: "https://en.wikipedia.org/wiki/Kullu_district"
  },

  lahaul_spiti: {
    name: "Lahaul & Spiti",
    hero: "./style/lahaul-spiti.jpg",
    hq: "Keylong",
    region: "Cold desert / Trans-Himalayan",
    knownFor: ["High passes", "Monasteries", "Cold desert landscapes"],
    about: [
      "Lahaul and Spiti is a high-altitude district known for cold-desert terrain, mountain passes, and a strong Buddhist cultural landscape in parts of the region.",
      "Use Balokhra as narrative inspiration; keep geography/admin facts aligned with Wikipedia."
    ],
    attractions: ["Keylong region", "High-altitude viewpoints", "Monastery circuits (as applicable)"],
    bestTime: ["Jun–Sep (most accessible)", "May/Oct (weather dependent)"],
    wiki: "https://en.wikipedia.org/wiki/Lahaul_and_Spiti_district"
  },

  mandi: {
    name: "Mandi",
    hero: "./style/mandi.jpg",
    hq: "Mandi",
    region: "Central Himachal / River valleys",
    knownFor: ["Temple town reputation", "Central connectivity", "River valley scenery"],
    about: [
      "Mandi is often described as centrally located in Himachal with a strong temple-town identity and valley scenery.",
      "Use Wikipedia for administration/geography facts and Balokhra for a ‘travelogue’ tone."
    ],
    attractions: ["Temple clusters", "Valley drives", "Local heritage areas"],
    bestTime: ["Oct–Mar", "Apr–Jun"],
    wiki: "https://en.wikipedia.org/wiki/Mandi_district"
  },

  shimla: {
    name: "Shimla",
    hero: "./style/shimla.jpg",
    hq: "Shimla",
    region: "Middle Himalayas",
    knownFor: ["State capital region", "Colonial-era heritage", "Ridge & hill circuits"],
    about: [
      "Shimla district includes the state-capital region and is a major tourism belt with heritage-era townscapes and surrounding hill circuits.",
      "Keep official facts aligned with Wikipedia; use Balokhra for a descriptive ‘Wonderland’ style travel writing."
    ],
    attractions: ["Heritage town areas", "Hill viewpoints", "Seasonal nature walks"],
    bestTime: ["Mar–Jun", "Oct–Dec"],
    wiki: "https://en.wikipedia.org/wiki/Shimla_district"
  },

  sirmaur: {
    name: "Sirmaur",
    hero: "./style/sirmaur.jpg",
    hq: "Nahan",
    region: "Shivalik / Southern Himachal",
    knownFor: ["Forested hills", "Nahan region", "Lower Himachal circuits"],
    about: [
      "Sirmaur lies in southern Himachal and includes Shivalik hill landscapes; Nahan is the district headquarters.",
      "Use Balokhra for narrative richness; verify all factual items via Wikipedia."
    ],
    attractions: ["Nahan & surroundings", "Forested hill spots", "Local temples"],
    bestTime: ["Oct–Mar", "Apr–Jun"],
    wiki: "https://en.wikipedia.org/wiki/Sirmaur_district"
  },

  solan: {
    name: "Solan",
    hero: "./style/solan.jpg",
    hq: "Solan",
    region: "Shivalik / Lower Himalayas",
    knownFor: ["Well-connected hill towns", "Mushroom/Agri identity in popular writing", "Easy access from Chandigarh side"],
    about: [
      "Solan district is a well-connected tourism + stay belt in lower Himachal, popular for short trips, hill-town weather, and gateway positioning.",
      "Use Wikipedia for district facts; use Balokhra as a descriptive reference."
    ],
    attractions: ["Hill-town viewpoints", "Local temples", "Short-drive picnic spots"],
    bestTime: ["Mar–Jun", "Oct–Dec"],
    wiki: "https://en.wikipedia.org/wiki/Solan_district"
  },

  una: {
    name: "Una",
    hero: "./style/una.jpg",
    hq: "Una",
    region: "Foothills / Lower Himachal",
    knownFor: ["Gateway district", "Foothill plains-to-hills transition", "Pilgrimage circuits nearby"],
    about: [
      "Una district sits in lower Himachal and is often treated as a gateway belt connecting plains travel routes with Himachal hill circuits.",
      "Write in tourism language (Balokhra-inspired), but keep facts aligned with Wikipedia."
    ],
    attractions: ["Temple visits (regional)", "Foothill drives", "Local markets"],
    bestTime: ["Oct–Mar", "Apr–Jun"],
    wiki: "https://en.wikipedia.org/wiki/Una_district"
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
}

window.renderDistrict = renderDistrict;
