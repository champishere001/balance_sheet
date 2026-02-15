const places=[

{n:"Shimla",d:"Shimla",img:"https://images.unsplash.com/photo-1589187151053-5ec8818e661b",lat:31.10,lon:77.17},
{n:"Manali",d:"Kullu",img:"https://images.unsplash.com/photo-1626621341517-bbf3d9990a23",lat:32.24,lon:77.19}

];

function getParam(name){
return new URLSearchParams(location.search).get(name);
}

function loadDistrict(){

let d=getParam("d");
document.getElementById("title").innerText=d;

let html="";
places.forEach(p=>{
if(p.d!==d)return;

html+=`
<a class="card" href="place.html?n=${p.n}">
<img src="${p.img}">
<div>${p.n}</div>
</a>`;
});

document.getElementById("grid").innerHTML=html;
}

function loadPlace(){

let n=getParam("n");
let p=places.find(x=>x.n===n);

document.getElementById("name").innerText=p.n;
document.getElementById("img").src=p.img;
document.getElementById("district").innerText=p.d;
document.getElementById("route").href=
`https://www.google.com/maps?q=${p.lat},${p.lon}`;

}

function calc(){
let p=+document.getElementById("p").value;
let d=+document.getElementById("d").value;
document.getElementById("total").innerText=
"Budget approx ₹"+(p*d*1500);
}