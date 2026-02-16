<script>
/**
 * HP Tourism demo data (You can expand anytime)
 * id must be unique. type: "place" | "hotel" | "temple" | "trek"
 */
window.HP_DATA = {
  districts: [
    { id:"shimla", name:"Shimla" },
    { id:"kullu", name:"Kullu" },
    { id:"kangra", name:"Kangra" },
    { id:"mandi", name:"Mandi" },
    { id:"chamba", name:"Chamba" }
  ],
  items: [
    // Places
    {
      id:"kufri",
      name:"Kufri",
      district:"shimla",
      type:"place",
      tags:["Snow","Family","Viewpoints"],
      short:"Famous for snow views, horse rides, and nearby forests.",
      img:"https://images.unsplash.com/photo-1588436706487-9d55d73a39e3?auto=format&fit=crop&w=1600&q=70",
      bestTime:"Dec–Feb (snow), Mar–Jun (pleasant)",
      highlights:["Mahasu Peak", "Kufri Fun World", "Views & trails"],
      nearby:["Shimla", "Naldehra"]
    },
    {
      id:"manali",
      name:"Manali",
      district:"kullu",
      type:"place",
      tags:["Adventure","Cafes","Snow"],
      short:"Iconic hill station with riverside vibes & adventure sports.",
      img:"https://images.unsplash.com/photo-1627920769842-6887c6df05ca?auto=format&fit=crop&w=1600&q=70",
      bestTime:"Oct–Feb (snow), Apr–Jun (summer)",
      highlights:["Old Manali", "Solang Valley", "Atal Tunnel route"],
      nearby:["Solang", "Kasol"]
    },
    {
      id:"dharamshala",
      name:"Dharamshala",
      district:"kangra",
      type:"place",
      tags:["Monasteries","Culture","Views"],
      short:"Tibetan culture, monasteries, and mountain views.",
      img:"https://images.unsplash.com/photo-1626497764746-6dc36546b388?auto=format&fit=crop&w=1600&q=70",
      bestTime:"Mar–Jun, Sep–Nov",
      highlights:["McLeod Ganj", "Monasteries", "Triund base"],
      nearby:["McLeod Ganj", "Kangra Fort"]
    },

    // Hotels (demo)
    {
      id:"hotel_shimla_view",
      name:"Hotel Shimla View (Demo)",
      district:"shimla",
      type:"hotel",
      tags:["3-Star","View","Parking"],
      short:"Cozy stay with valley views (demo listing).",
      img:"https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=1600&q=70",
      priceFrom:2200
    },
    {
      id:"hotel_kullu_river",
      name:"Kullu Riverside Stay (Demo)",
      district:"kullu",
      type:"hotel",
      tags:["Budget","River","Cafe"],
      short:"Riverside vibes + mountain air (demo listing).",
      img:"https://images.unsplash.com/photo-1512918728675-ed5a9ecdebfd?auto=format&fit=crop&w=1600&q=70",
      priceFrom:1800
    },

    // Temples (demo)
    {
      id:"jakhoo",
      name:"Jakhoo Temple",
      district:"shimla",
      type:"temple",
      tags:["Hanuman","Top View","Ropeway"],
      short:"Famous hilltop Hanuman temple with panoramic views.",
      img:"https://images.unsplash.com/photo-1590134001156-0a6a4f3f2b6b?auto=format&fit=crop&w=1600&q=70"
    },
    {
      id:"baijnath",
      name:"Baijnath Temple",
      district:"kangra",
      type:"temple",
      tags:["Shiva","Heritage","Architecture"],
      short:"Ancient Shiva temple known for stone architecture.",
      img:"https://images.unsplash.com/photo-1582719478185-2f5b0a4b5c0a?auto=format&fit=crop&w=1600&q=70"
    },

    // Treks (demo)
    {
      id:"triund",
      name:"Triund Trek",
      district:"kangra",
      type:"trek",
      tags:["Beginner","View","Overnight"],
      short:"Classic trek near McLeod Ganj with stunning ridge views.",
      img:"https://images.unsplash.com/photo-1526481280695-3c687fd5432c?auto=format&fit=crop&w=1600&q=70",
      difficulty:"Easy–Moderate"
    },
    {
      id:"hampta",
      name:"Hampta Pass (Demo)",
      district:"kullu",
      type:"trek",
      tags:["Pass","Camping","Adventure"],
      short:"High mountain pass trek (demo listing).",
      img:"https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1600&q=70",
      difficulty:"Moderate"
    }
  ],

  // Simple distance matrix (km) for calculator demo (expand later)
  distances_km: {
    "shimla:kufri": 16,
    "kullu:manali": 40,
    "kangra:dharamshala": 18,
    "shimla:jakhoo": 5,
    "kangra:triund": 9
  }
};
</script>
