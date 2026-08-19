import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="DragonNinja", page_icon="🐉", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
.stApp {
    background: radial-gradient(circle at 20% 20%, #1a0b2e 0%, #0d0518 50%, #050208 100%);
}
#MainMenu, footer, header {visibility: hidden;}
.title-wrap { text-align: center; padding: 8px 0 4px 0; }
.title-wrap h1 {
    background: linear-gradient(90deg, #ff4d4d, #ff9d00, #7c3aed, #06b6d4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-weight: 800; font-size: 2.6rem; margin-bottom: 0; letter-spacing: 1px;
}
.subtitle { text-align: center; color: #a78bfa; font-weight: 300; margin-top: -8px; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="title-wrap"><h1>🐉 DRAGON NINJA 🥷</h1></div>
<div class="subtitle">Slash. Dash. Breathe fire. Face five guardians of the temple.</div>
""", unsafe_allow_html=True)

GAME_HTML = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * { box-sizing: border-box; margin:0; padding:0; }
  body { font-family: 'Outfit', sans-serif; display:flex; flex-direction:column; align-items:center; background: transparent; }
  #gameWrap {
    position: relative; width: 900px; max-width: 100%;
    border-radius: 16px; overflow: hidden;
    box-shadow: 0 0 40px rgba(124,58,237,0.35), 0 0 0 1px rgba(255,255,255,0.08);
  }
  canvas { display:block; width: 100%; background: linear-gradient(180deg,#150a2e 0%, #2a1450 55%, #3d1a4a 100%); }
  #hud {
    position:absolute; top:10px; left:10px; right:10px;
    display:flex; justify-content:space-between; align-items:flex-start;
    pointer-events:none; color:#fff; font-family:'Outfit',sans-serif;
  }
  .panel {
    background: rgba(10,5,25,0.55); backdrop-filter: blur(6px);
    border: 1px solid rgba(255,255,255,0.12); border-radius: 10px;
    padding: 8px 12px; font-size: 13px;
  }
  .barBg { width: 160px; height: 12px; border-radius:6px; background: rgba(255,255,255,0.1); overflow:hidden; margin-top:4px; }
  .barFill { height:100%; border-radius:6px; transition: width 0.15s; }
  #hpFill { background: linear-gradient(90deg,#ff4d6d,#ff9d00); }
  #chiFill { background: linear-gradient(90deg,#06b6d4,#7c3aed); }
  #overlay {
    position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center;
    background: rgba(5,2,15,0.85); color:#fff; text-align:center; gap:10px; padding:20px;
  }
  #overlay h2 { font-size:30px; background: linear-gradient(90deg,#ff4d4d,#ff9d00,#7c3aed);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
  #overlay p { color:#c4b5fd; max-width:520px; font-size:14px; line-height:1.5; }
  button.gbtn {
    margin-top:8px; background: linear-gradient(90deg,#7c3aed,#06b6d4); border:none; color:#fff;
    padding:10px 24px; border-radius:24px; font-size:15px; font-weight:600; cursor:pointer; font-family:'Outfit',sans-serif;
  }
  button.gbtn:hover { filter: brightness(1.15); }
  #controls { margin-top:10px; color:#a78bfa; font-size:12.5px; text-align:center; line-height:1.6; }
  #controls b { color:#e9d5ff; }
  #progressDots { display:flex; gap:6px; margin-top:6px; flex-wrap:wrap; justify-content:center; max-width:480px; }
  .dot { width:10px; height:10px; border-radius:50%; background: rgba(255,255,255,0.15); }
  .dot.boss { background: rgba(255,77,77,0.3); }
  .dot.done { background: #06b6d4; }
  .dot.bossdone { background: #ff4d4d; }
</style>
</head>
<body>
<div id="gameWrap">
  <canvas id="game" width="900" height="500"></canvas>
  <div id="hud">
    <div class="panel">
      <div>❤️ Health</div>
      <div class="barBg"><div class="barFill" id="hpFill" style="width:100%"></div></div>
    </div>
    <div class="panel" style="text-align:right;">
      <div>Level <span id="lvl">1</span>/<span id="lvlTotal">11</span> — Scrolls: <span id="scrolls">0</span>/<span id="scrollsTotal">5</span></div>
      <div style="margin-top:2px;">🔥 Chi</div>
      <div class="barBg"><div class="barFill" id="chiFill" style="width:100%"></div></div>
    </div>
  </div>
  <div id="overlay">
    <h2>🐉 DRAGON NINJA 🥷</h2>
    <p>You are the last Dragon Ninja. Cut through the temple's halls, gather ancient scrolls,
       and defeat all <b>five Guardians</b> standing between you and the Dragon Throne.</p>
    <div id="controls">
      <b>← → / A D</b> Move &nbsp;•&nbsp; <b>SPACE / W</b> Jump (double-jump!) &nbsp;•&nbsp; <b>J</b> Sword Slash<br>
      <b>K</b> Fire Breath (uses Chi) &nbsp;•&nbsp; <b>SHIFT</b> Dash (brief invulnerability)
    </div>
    <button class="gbtn" id="startBtn">Begin Journey</button>
  </div>
</div>

<script>
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const W = canvas.width, H = canvas.height;
const GRAVITY = 0.62;

let keys = {};
document.addEventListener('keydown', e => {
  keys[e.key.toLowerCase()] = true;
  if(['arrowup','arrowdown','arrowleft','arrowright',' '].includes(e.key.toLowerCase())) e.preventDefault();
});
document.addEventListener('keyup', e => keys[e.key.toLowerCase()] = false);

function rectsOverlap(a,b){
  return a.x < b.x+b.w && a.x+a.w > b.x && a.y < b.y+b.h && a.y+a.h > b.y;
}

// ---------- Level Data ----------
// type: 'normal' or 'boss'
function buildLevels(){
  return [
    { type:'normal',
      platforms: [
        {x:0,y:460,w:900,h:40}, {x:150,y:370,w:120,h:20}, {x:340,y:300,w:120,h:20},
        {x:540,y:250,w:120,h:20}, {x:700,y:380,w:150,h:20}
      ],
      enemies: [
        {x:400,y:270,w:34,h:40,vx:1.4,range:[340,460],hp:2,type:'shadow'},
        {x:750,y:350,w:34,h:40,vx:1.2,range:[700,840],hp:2,type:'shadow'}
      ],
      scrolls: [{x:190,y:335,taken:false},{x:600,y:215,taken:false}],
      spawn:{x:30,y:400}, goal:{x:775,y:330,w:50,h:44}
    },
    { type:'normal',
      platforms: [
        {x:0,y:460,w:900,h:40}, {x:120,y:400,w:100,h:20}, {x:280,y:340,w:100,h:20},
        {x:440,y:280,w:100,h:20}, {x:600,y:340,w:100,h:20}, {x:760,y:400,w:100,h:20},
        {x:200,y:220,w:120,h:20}, {x:500,y:160,w:140,h:20}
      ],
      enemies: [
        {x:300,y:310,w:34,h:40,vx:1.6,range:[280,380],hp:2,type:'shadow'},
        {x:620,y:310,w:34,h:40,vx:1.6,range:[600,700],hp:2,type:'shadow'},
        {x:230,y:190,w:34,h:40,vx:1.3,range:[200,320],hp:3,type:'archer'}
      ],
      scrolls: [{x:250,y:185,taken:false},{x:540,y:125,taken:false},{x:460,y:245,taken:false}],
      spawn:{x:30,y:400}, goal:{x:790,y:350,w:50,h:50}
    },
    { type:'normal',
      platforms: [
        {x:0,y:460,w:900,h:40}, {x:130,y:390,w:90,h:20}, {x:280,y:420,w:90,h:20},
        {x:430,y:350,w:90,h:20}, {x:580,y:290,w:90,h:20}, {x:720,y:230,w:120,h:20}
      ],
      enemies: [
        {x:300,y:390,w:34,h:40,vx:1.5,range:[280,370],hp:2,type:'shadow'},
        {x:600,y:260,w:34,h:40,vx:1.4,range:[580,670],hp:3,type:'archer'}
      ],
      scrolls: [{x:160,y:355,taken:false},{x:450,y:315,taken:false},{x:750,y:195,taken:false}],
      spawn:{x:30,y:400}, goal:{x:770,y:190,w:50,h:40}
    },
    { type:'boss', bossType:'guardian', bossName:'Temple Guardian', bossHp:55, bossColor:'#ff4d4d',
      platforms: [{x:0,y:460,w:900,h:40},{x:770,y:340,w:100,h:20}],
      scrolls: [{x:100,y:390,taken:false}],
      spawn:{x:50,y:400}, goal:{x:795,y:300,w:50,h:40}
    },
    { type:'normal',
      platforms: [
        {x:0,y:460,w:900,h:40}, {x:100,y:400,w:90,h:20}, {x:250,y:350,w:90,h:20},
        {x:400,y:400,w:90,h:20}, {x:550,y:320,w:90,h:20}, {x:700,y:260,w:90,h:20},
        {x:400,y:200,w:120,h:20}
      ],
      enemies: [
        {x:270,y:320,w:34,h:40,vx:1.8,range:[250,340],hp:2,type:'shadow'},
        {x:420,y:200,w:34,h:40,vx:1.4,range:[400,520],hp:3,type:'archer'},
        {x:720,y:230,w:34,h:40,vx:1.5,range:[700,790],hp:2,type:'shadow'}
      ],
      scrolls: [{x:130,y:365,taken:false},{x:440,y:165,taken:false}],
      spawn:{x:30,y:400}, goal:{x:725,y:220,w:50,h:40}
    },
    { type:'normal',
      platforms: [
        {x:0,y:460,w:900,h:40}, {x:110,y:410,w:80,h:20}, {x:230,y:360,w:80,h:20},
        {x:350,y:410,w:80,h:20}, {x:480,y:330,w:80,h:20}, {x:610,y:260,w:80,h:20},
        {x:750,y:200,w:120,h:20}
      ],
      enemies: [
        {x:250,y:330,w:34,h:40,vx:1.6,range:[230,300],hp:2,type:'shadow'},
        {x:500,y:300,w:34,h:40,vx:1.3,range:[480,550],hp:3,type:'archer'},
        {x:630,y:230,w:34,h:40,vx:1.7,range:[610,680],hp:3,type:'shadow'}
      ],
      scrolls: [{x:140,y:375,taken:false},{x:640,y:225,taken:false},{x:780,y:165,taken:false}],
      spawn:{x:30,y:400}, goal:{x:800,y:160,w:50,h:40}
    },
    { type:'boss', bossType:'assassin', bossName:'Shadow Assassin', bossHp:65, bossColor:'#7c3aed',
      platforms: [{x:0,y:460,w:900,h:40},{x:150,y:340,w:140,h:20},{x:610,y:340,w:140,h:20}],
      scrolls: [{x:840,y:390,taken:false}],
      spawn:{x:50,y:400}, goal:{x:635,y:300,w:50,h:40}
    },
    { type:'normal',
      platforms: [
        {x:0,y:460,w:900,h:40}, {x:180,y:390,w:100,h:20}, {x:360,y:330,w:100,h:20},
        {x:540,y:270,w:100,h:20}, {x:700,y:220,w:100,h:20}, {x:80,y:230,w:100,h:20}
      ],
      enemies: [
        {x:380,y:300,w:34,h:40,vx:1.7,range:[360,460],hp:3,type:'shadow'},
        {x:560,y:240,w:34,h:40,vx:1.5,range:[540,640],hp:3,type:'shadow'},
        {x:100,y:200,w:34,h:40,vx:1.3,range:[80,180],hp:3,type:'archer'}
      ],
      scrolls: [{x:210,y:355,taken:false},{x:110,y:195,taken:false}],
      spawn:{x:30,y:400}, goal:{x:725,y:180,w:50,h:40}
    },
    { type:'boss', bossType:'golem', bossName:'Stone Golem', bossHp:90, bossColor:'#9ca3af',
      platforms: [{x:0,y:460,w:900,h:40},{x:770,y:360,w:100,h:20}],
      scrolls: [{x:450,y:390,taken:false}],
      spawn:{x:50,y:400}, goal:{x:795,y:320,w:50,h:40}
    },
    { type:'normal',
      platforms: [
        {x:0,y:460,w:900,h:40}, {x:120,y:410,w:80,h:20}, {x:260,y:350,w:80,h:20},
        {x:400,y:290,w:80,h:20}, {x:540,y:230,w:80,h:20}, {x:680,y:170,w:80,h:20},
        {x:780,y:400,w:100,h:20}
      ],
      enemies: [
        {x:280,y:320,w:34,h:40,vx:1.8,range:[260,340],hp:3,type:'shadow'},
        {x:420,y:260,w:34,h:40,vx:1.3,range:[400,480],hp:3,type:'archer'},
        {x:560,y:200,w:34,h:40,vx:1.9,range:[540,620],hp:3,type:'shadow'},
        {x:700,y:140,w:34,h:40,vx:1.4,range:[680,760],hp:4,type:'archer'}
      ],
      scrolls: [{x:150,y:375,taken:false},{x:570,y:195,taken:false},{x:710,y:135,taken:false}],
      spawn:{x:30,y:400}, goal:{x:700,y:130,w:50,h:40}
    },
    { type:'normal',
      platforms: [
        {x:0,y:460,w:900,h:40}, {x:140,y:410,w:90,h:20}, {x:300,y:350,w:90,h:20},
        {x:460,y:400,w:90,h:20}, {x:610,y:330,w:90,h:20}, {x:760,y:260,w:120,h:20}
      ],
      enemies: [
        {x:320,y:320,w:34,h:40,vx:1.7,range:[300,390],hp:3,type:'shadow'},
        {x:630,y:300,w:34,h:40,vx:1.5,range:[610,700],hp:3,type:'archer'}
      ],
      scrolls: [{x:170,y:375,taken:false},{x:490,y:365,taken:false},{x:800,y:225,taken:false}],
      spawn:{x:30,y:400}, goal:{x:790,y:220,w:50,h:40}
    },
    { type:'boss', bossType:'phoenix', bossName:'Phoenix Sentinel', bossHp:85, bossColor:'#ff9d00',
      platforms: [{x:0,y:460,w:900,h:40},{x:100,y:340,w:120,h:20},{x:680,y:340,w:120,h:20},{x:390,y:260,w:120,h:20}],
      scrolls: [{x:430,y:225,taken:false}],
      spawn:{x:50,y:400}, goal:{x:715,y:300,w:50,h:40}
    },
    { type:'normal',
      platforms: [
        {x:0,y:460,w:900,h:40}, {x:140,y:400,w:90,h:20}, {x:300,y:340,w:90,h:20},
        {x:460,y:280,w:90,h:20}, {x:620,y:340,w:90,h:20}, {x:770,y:400,w:90,h:20},
        {x:250,y:200,w:100,h:20}, {x:550,y:160,w:120,h:20}
      ],
      enemies: [
        {x:320,y:310,w:34,h:40,vx:2.0,range:[300,390],hp:3,type:'shadow'},
        {x:640,y:310,w:34,h:40,vx:2.0,range:[620,710],hp:3,type:'shadow'},
        {x:280,y:170,w:34,h:40,vx:1.5,range:[250,350],hp:4,type:'archer'},
        {x:580,y:130,w:34,h:40,vx:1.5,range:[550,670],hp:4,type:'archer'}
      ],
      scrolls: [{x:170,y:365,taken:false},{x:300,y:165,taken:false},{x:600,y:125,taken:false},{x:480,y:245,taken:false}],
      spawn:{x:30,y:400}, goal:{x:580,y:120,w:50,h:40}
    },
    { type:'normal',
      platforms: [
        {x:0,y:460,w:900,h:40}, {x:150,y:400,w:90,h:20}, {x:320,y:340,w:90,h:20},
        {x:490,y:280,w:90,h:20}, {x:650,y:220,w:90,h:20}, {x:790,y:160,w:100,h:20}
      ],
      enemies: [
        {x:340,y:310,w:34,h:40,vx:2.0,range:[320,410],hp:4,type:'shadow'},
        {x:510,y:250,w:34,h:40,vx:1.6,range:[490,580],hp:4,type:'archer'},
        {x:670,y:190,w:34,h:40,vx:1.9,range:[650,740],hp:4,type:'shadow'}
      ],
      scrolls: [{x:180,y:365,taken:false},{x:670,y:185,taken:false},{x:820,y:125,taken:false}],
      spawn:{x:30,y:400}, goal:{x:810,y:120,w:50,h:40}
    },
    { type:'boss', bossType:'emperor', bossName:'Dragon Emperor', bossHp:140, bossColor:'#ef233c',
      platforms: [{x:0,y:460,w:900,h:40},{x:180,y:360,w:120,h:20},{x:600,y:360,w:120,h:20}],
      scrolls: [{x:420,y:400,taken:false}],
      spawn:{x:50,y:400}, goal:{x:415,y:320,w:50,h:40}
    }
  ];
}

let levels = buildLevels();
let levelIdx = 0;
let level = levels[0];
document.getElementById('lvlTotal').innerText = levels.length;

// ---------- Player ----------
const player = {
  x:30,y:400,w:34,h:44,vx:0,vy:0,
  onGround:false, facing:1, hp:100, maxHp:100, chi:100, maxChi:100,
  jumps:0, maxJumps:2, dashCd:0, slashCd:0, breathCd:0,
  slashTimer:0, invuln:0, breathTimer:0
};

let particles = [];
let projectiles = [];
let fireballs = [];
let scrollsCollected = 0;
let gameState = 'menu';
let camShake = 0;
let bossesDefeated = 0;

// boss runtime state
let boss = null;

function makeBoss(def){
  return {
    type: def.bossType, name: def.bossName, color: def.bossColor,
    hp: def.bossHp, maxHp: def.bossHp,
    x: 620, y: 380, w: 70, h: 80, vx: -1.5, phase: 1,
    attackCd: 90, teleportCd: 140, telegraph:0, target:{x:620,y:380},
    dashing:false, dashTimer:0, minionsSpawned:false
  };
}

function resetLevel(idx){
  const raw = levels[idx];
  level = JSON.parse(JSON.stringify(raw));
  player.x = level.spawn.x; player.y = level.spawn.y;
  player.vx=0; player.vy=0; player.jumps=0; player.invuln=60;
  projectiles = []; fireballs = []; particles=[];
  if(level.type==='boss'){
    boss = makeBoss(level);
  } else { boss = null; }
  document.getElementById('lvl').innerText = idx+1;
  document.getElementById('scrollsTotal').innerText = level.scrolls.length;
  document.getElementById('scrolls').innerText = '0';
}

function startGame(){
  levelIdx = 0;
  player.hp = player.maxHp; player.chi = player.maxChi;
  scrollsCollected = 0; bossesDefeated = 0;
  resetLevel(0);
  gameState = 'playing';
  document.getElementById('overlay').style.display='none';
}

document.getElementById('startBtn').addEventListener('click', startGame);

function spawnParticles(x,y,color,n,spread){
  for(let i=0;i<n;i++){
    particles.push({x,y,vx:(Math.random()-0.5)*spread,vy:(Math.random()-0.5)*spread-1,life:30+Math.random()*20,color});
  }
}

function playerSlashHits(target){
  if(player.slashTimer>0){
    const reach = {x: player.facing>0?player.x+player.w:player.x-30, y:player.y, w:30, h:player.h};
    return rectsOverlap(reach, target);
  }
  return false;
}

function updateBoss(){
  if(!boss || boss.hp<=0) return;
  const bx = {x:boss.x,y:boss.y,w:boss.w,h:boss.h};

  if(boss.type==='guardian'){
    let dx = player.x - boss.x;
    if(Math.abs(dx)>60) boss.x += Math.sign(dx)*1.6*boss.phase;
    boss.x = Math.max(20, Math.min(W-90, boss.x));
    boss.attackCd--;
    if(boss.attackCd<=0){
      boss.attackCd = boss.phase===1?80:50;
      for(let a=-1;a<=1;a++){
        projectiles.push({x:boss.x+35,y:boss.y+20,vx:a*4+(player.x>boss.x?2:-2),vy:-6,life:200,grav:true});
      }
    }
  }
  else if(boss.type==='assassin'){
    boss.teleportCd--;
    if(boss.teleportCd<=0 && !boss.dashing){
      boss.teleportCd = 110;
      spawnParticles(boss.x+35,boss.y+40,'#7c3aed',12,6);
      boss.x = Math.max(20,Math.min(W-90, player.x + (Math.random()<0.5?-140:140)));
      boss.y = 380;
      boss.dashing = true; boss.dashTimer = 26;
      spawnParticles(boss.x+35,boss.y+40,'#c4b5fd',12,6);
    }
    if(boss.dashing){
      boss.dashTimer--;
      let dir = Math.sign((player.x+17) - (boss.x+35)) || 1;
      boss.x += dir*7;
      if(boss.dashTimer<=0) boss.dashing=false;
    }
    boss.x = Math.max(20, Math.min(W-90, boss.x));
  }
  else if(boss.type==='golem'){
    let dx = player.x - boss.x;
    if(Math.abs(dx)>50) boss.x += Math.sign(dx)*0.9;
    boss.x = Math.max(20, Math.min(W-90, boss.x));
    boss.attackCd--;
    if(boss.attackCd<=0){
      boss.attackCd = boss.phase===1?110:75;
      camShake = 14;
      // shockwave: line of projectiles along ground moving both directions
      for(let i=1;i<=5;i++){
        projectiles.push({x:boss.x+35-i*22,y:445,vx:-2,vy:0,life:60,ground:true});
        projectiles.push({x:boss.x+35+i*22,y:445,vx:2,vy:0,life:60,ground:true});
      }
    }
  }
  else if(boss.type==='phoenix'){
    boss.telegraph = boss.telegraph||0;
    let t = Date.now()/500;
    boss.x = 400 + Math.sin(t)*300;
    boss.y = 150 + Math.sin(t*1.7)*40;
    boss.attackCd--;
    if(boss.attackCd<=0){
      boss.attackCd = boss.phase===1?70:45;
      for(let i=0;i<3;i++){
        projectiles.push({x:boss.x+35+(i-1)*20,y:boss.y+60,vx:(i-1)*1.5,vy:4,life:150,grav:false,fire:true});
      }
    }
  }
  else if(boss.type==='emperor'){
    let dx = player.x - boss.x;
    if(!boss.dashing && Math.abs(dx)>70) boss.x += Math.sign(dx)*1.3*boss.phase;
    boss.x = Math.max(20, Math.min(W-90, boss.x));
    boss.attackCd--;
    if(boss.attackCd<=0){
      boss.attackCd = boss.phase===1?70:42;
      let choice = Math.random();
      if(choice<0.5){
        for(let a=-2;a<=2;a++){
          projectiles.push({x:boss.x+35,y:boss.y+20,vx:a*3.5,vy:-5,life:200,grav:true});
        }
      } else {
        boss.dashing = true; boss.dashTimer = 20;
        spawnParticles(boss.x+35,boss.y+40,'#ef233c',10,5);
      }
    }
    if(boss.dashing){
      boss.dashTimer--;
      let dir = Math.sign((player.x+17)-(boss.x+35)) || 1;
      boss.x += dir*9;
      if(boss.dashTimer<=0) boss.dashing=false;
    }
  }

  if(boss.hp <= boss.maxHp/2) boss.phase = 2;

  // contact damage
  if(rectsOverlap(player,bx) && player.invuln<=0){
    player.hp -= (boss.type==='golem'?9: boss.type==='emperor'?9:7);
    player.invuln = 45; camShake = 10;
    spawnParticles(player.x+player.w/2,player.y+player.h/2,'#ff4d6d',8,4);
  }
  // player slash damage
  if(playerSlashHits(bx)){
    let dmg = 1.6;
    boss.hp -= dmg;
    spawnParticles(boss.x+35,boss.y+40,'#ff9d00',5,4);
  }

  if(boss.hp<=0){
    if(!level.bossDefeated){
      level.bossDefeated = true;
      bossesDefeated++;
      spawnParticles(boss.x+35,boss.y+40,boss.color,30,8);
    }
  }
}

function update(){
  if(gameState !== 'playing') return;

  let speed = 4.2;
  if(keys['a']||keys['arrowleft']){ player.vx = -speed; player.facing=-1; }
  else if(keys['d']||keys['arrowright']){ player.vx = speed; player.facing=1; }
  else { player.vx *= 0.75; }

  if((keys[' ']||keys['w']||keys['arrowup']) && player.jumps < player.maxJumps && !player._jumpHeld){
    player.vy = -12.5; player.jumps++; player._jumpHeld = true;
    spawnParticles(player.x+player.w/2, player.y+player.h, '#a78bfa', 6, 3);
  }
  if(!(keys[' ']||keys['w']||keys['arrowup'])) player._jumpHeld = false;

  if(keys['shift'] && player.dashCd<=0){
    player.vx = 14*player.facing; player.dashCd = 45; player.invuln = 12;
    spawnParticles(player.x+player.w/2, player.y+player.h/2, '#06b6d4', 10, 5);
  }
  if(player.dashCd>0) player.dashCd--;

  if(keys['j'] && player.slashCd<=0){ player.slashCd = 22; player.slashTimer = 10; }
  if(player.slashCd>0) player.slashCd--;
  if(player.slashTimer>0) player.slashTimer--;

  if(keys['k'] && player.breathCd<=0 && player.chi>=18){
    player.breathCd = 8; player.chi -= 1.2; player.breathTimer = 14;
    fireballs.push({x:player.x+player.w/2+player.facing*20, y:player.y+18, vx:player.facing*9+player.vx*0.3, vy:(Math.random()-0.5)*1.5, life:40});
  }
  if(player.breathCd>0) player.breathCd--;
  if(player.breathTimer>0) player.breathTimer--;
  if(player.chi < player.maxChi) player.chi += 0.08;

  player.vy += GRAVITY;
  if(player.vy>16) player.vy=16;
  player.x += player.vx;
  player.y += player.vy;

  player.onGround = false;
  for(const p of level.platforms){
    if(rectsOverlap(player,p)){
      const prevBottom = player.y - player.vy;
      if(prevBottom <= p.y && player.vy>=0){
        player.y = p.y - player.h; player.vy=0; player.onGround=true; player.jumps=0;
      } else if(player.vy<0 && player.y >= p.y+p.h-player.h - 30 - player.vy){
        player.y = p.y+p.h; player.vy = 1;
      } else {
        if(player.x + player.w/2 < p.x + p.w/2) player.x = p.x - player.w;
        else player.x = p.x + p.w;
      }
    }
  }
  if(player.x<0) player.x=0;
  if(player.x+player.w>W) player.x=W-player.w;
  if(player.y>H+100){ player.hp -= 100; }
  if(player.invuln>0) player.invuln--;

  if(level.type==='normal'){
    for(const e of level.enemies){
      if(e.hp<=0) continue;
      if(e.type==='shadow'){
        e.x += e.vx;
        if(e.x<e.range[0]||e.x+e.w>e.range[1]) e.vx*=-1;
        if(Math.abs((e.x+e.w/2)-(player.x+player.w/2))<40 && Math.abs(e.y-player.y)<50 && player.invuln<=0 && Math.random()<0.03){
          player.hp -= 6; player.invuln=40; camShake=8;
          spawnParticles(player.x+player.w/2,player.y+player.h/2,'#ff4d6d',8,4);
        }
      } else if(e.type==='archer'){
        e.x += e.vx;
        if(e.x<e.range[0]||e.x+e.w>e.range[1]) e.vx*=-1;
        e.shootCd = (e.shootCd||0)-1;
        if(e.shootCd<=0){
          e.shootCd = 90;
          let dir = (player.x > e.x)?1:-1;
          projectiles.push({x:e.x+e.w/2,y:e.y+e.h/2,vx:dir*6,vy:0,life:120});
        }
      }
      if(playerSlashHits(e)){
        e.hp -= 1;
        spawnParticles(e.x+e.w/2,e.y+e.h/2,'#ff9d00',6,4);
      }
      if(rectsOverlap(player,e) && player.invuln<=0){
        player.hp -= 8; player.invuln=45; camShake=8;
      }
    }
  }

  for(const fb of fireballs){
    fb.x += fb.vx; fb.y += fb.vy; fb.life--;
    if(level.type==='normal'){
      for(const e of level.enemies){
        if(e.hp>0 && rectsOverlap({x:fb.x-8,y:fb.y-8,w:16,h:16}, e)){
          e.hp -= 2; fb.life=0;
          spawnParticles(e.x+e.w/2,e.y+e.h/2,'#ff6b00',10,5);
        }
      }
    } else if(boss && boss.hp>0 && rectsOverlap({x:fb.x-8,y:fb.y-8,w:16,h:16},{x:boss.x,y:boss.y,w:boss.w,h:boss.h})){
      boss.hp -= 4.5; fb.life=0;
      spawnParticles(boss.x+35,boss.y+40,'#ff6b00',10,5);
    }
  }
  fireballs = fireballs.filter(f=>f.life>0);

  for(const pr of projectiles){
    pr.x += pr.vx; if(pr.grav) pr.vy += 0.25;
    pr.y += pr.vy || 0;
    pr.life--;
    if(rectsOverlap({x:pr.x-4,y:pr.y-4,w:8,h:8}, player) && player.invuln<=0){
      player.hp -= (pr.fire?6:7); player.invuln=40; pr.life=0; camShake=8;
    }
  }
  projectiles = projectiles.filter(p=>p.life>0);

  for(const s of level.scrolls){
    if(!s.taken && rectsOverlap({x:s.x,y:s.y,w:20,h:20}, player)){
      s.taken = true; scrollsCollected++;
      document.getElementById('scrolls').innerText = level.scrolls.filter(x=>x.taken).length;
      spawnParticles(s.x+10,s.y+10,'#ffd700',14,5);
    }
  }

  for(const p of particles){ p.x+=p.vx; p.y+=p.vy; p.vy+=0.15; p.life--; }
  particles = particles.filter(p=>p.life>0);

  if(level.type==='boss'){
    updateBoss();
    if(level.bossDefeated && rectsOverlap(player, level.goal)){
      gameState='levelclear';
      let allScrolls = level.scrolls.every(s=>s.taken);
      let isFinal = levelIdx === levels.length-1;
      showOverlay(isFinal ? '🐉 TEMPLE RESTORED! 🐉' : ('⚔️ '+level.bossName+' Defeated!'),
        isFinal ? ('You have defeated all five Guardians and reclaimed the Dragon Throne. Total scrolls collected: '+scrollsCollected)
                : ((allScrolls?'All scrolls collected! ':'')+'Bosses defeated: '+bossesDefeated+'/5'),
        isFinal ? 'Play Again' : 'Continue');
      if(isFinal) gameState='won';
    }
  } else if(rectsOverlap(player, level.goal)){
    gameState='levelclear';
    let allScrolls = level.scrolls.every(s=>s.taken);
    showOverlay('Level Complete!', allScrolls? 'All scrolls collected! Bonus chi restored.' : 'Gate reached. Some scrolls remain hidden in the shadows.', 'Continue');
    if(allScrolls) player.chi = player.maxChi;
  }

  if(player.hp<=0){
    gameState='dead';
    showOverlay('💀 You Have Fallen', 'Total scrolls collected: '+scrollsCollected+' • Bosses defeated: '+bossesDefeated+'/5', 'Retry Level');
  }

  if(camShake>0) camShake -= 0.6;

  document.getElementById('hpFill').style.width = Math.max(0,player.hp)+'%';
  document.getElementById('chiFill').style.width = Math.max(0,player.chi)+'%';
}

function showOverlay(title, text, btnLabel){
  const ov = document.getElementById('overlay');
  ov.innerHTML = `<h2>${title}</h2><p>${text}</p><button class="gbtn" id="ovBtn">${btnLabel}</button>`;
  ov.style.display='flex';
  document.getElementById('ovBtn').addEventListener('click', ()=>{
    if(gameState==='dead'){ resetLevel(levelIdx); gameState='playing'; ov.style.display='none'; }
    else if(gameState==='levelclear'){
      levelIdx++;
      if(levelIdx>=levels.length){
        showOverlay('🐉 TEMPLE RESTORED! 🐉',
          'You have defeated all five Guardians and reclaimed the Dragon Throne. Total scrolls collected: '+scrollsCollected,
          'Play Again');
        gameState='won';
        return;
      }
      resetLevel(levelIdx); gameState='playing'; ov.style.display='none';
    } else if(gameState==='won'){ startGame(); }
  });
}

// ---------- Draw ----------
function drawPlayer(){
  ctx.save();
  let sx = player.x+player.w/2, sy=player.y+player.h/2;
  ctx.translate(sx,sy);
  ctx.scale(player.facing,1);
  ctx.translate(-player.w/2,-player.h/2);
  if(player.invuln>0 && Math.floor(player.invuln/4)%2===0){ ctx.globalAlpha = 0.5; }
  ctx.fillStyle = '#1e1030';
  ctx.fillRect(4,10,player.w-8,player.h-14);
  ctx.fillStyle = '#7c3aed';
  ctx.fillRect(4,10,player.w-8,6);
  ctx.fillStyle = '#2a1a40';
  ctx.fillRect(6,0,player.w-12,14);
  ctx.fillStyle = '#ff9d00';
  ctx.fillRect(player.w-14,5,4,3);
  ctx.fillStyle = '#150a20';
  ctx.fillRect(6,player.h-10,8,10);
  ctx.fillRect(player.w-14,player.h-10,8,10);
  if(player.slashTimer>0){
    ctx.globalAlpha = player.slashTimer/10;
    ctx.strokeStyle = '#ffd700';
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.arc(player.w, player.h/2, 26, -0.8, 0.8);
    ctx.stroke();
    ctx.globalAlpha=1;
  }
  ctx.restore();
}

function drawEnemy(e){
  if(e.hp<=0) return;
  ctx.save();
  ctx.fillStyle = e.type==='archer' ? '#4a1d6b' : '#2d0f45';
  ctx.fillRect(e.x,e.y,e.w,e.h);
  ctx.fillStyle = '#ff4d4d';
  ctx.fillRect(e.x+e.w-10,e.y+6,5,4);
  for(let i=0;i<e.hp;i++){
    ctx.fillStyle='#ff4d6d';
    ctx.fillRect(e.x+i*8, e.y-8, 6,4);
  }
  ctx.restore();
}

function drawBoss(){
  if(!boss || boss.hp<=0) return;
  ctx.save();
  ctx.fillStyle = boss.color;
  ctx.globalAlpha = 0.9;
  ctx.fillRect(boss.x,boss.y,boss.w,boss.h);
  ctx.globalAlpha = 1;
  ctx.fillStyle = '#000';
  ctx.fillRect(boss.x+50,boss.y+10,10,8);
  ctx.fillRect(boss.x+10,boss.y+10,10,8);
  ctx.fillStyle='#fff';
  ctx.fillRect(boss.x+15,boss.y+13,4,3);
  ctx.fillRect(boss.x+53,boss.y+13,4,3);
  ctx.restore();

  ctx.fillStyle = 'rgba(255,255,255,0.15)';
  ctx.fillRect(W/2-150,20,300,14);
  ctx.fillStyle = boss.color;
  ctx.fillRect(W/2-150,20,300*Math.max(0,boss.hp/boss.maxHp),14);
  ctx.strokeStyle='rgba(255,255,255,0.4)';
  ctx.strokeRect(W/2-150,20,300,14);
  ctx.fillStyle='#fff'; ctx.font='12px Outfit'; ctx.textAlign='center';
  ctx.fillText(boss.name+' — Phase '+boss.phase, W/2, 16);
}

function drawGoal(g, active){
  ctx.save();
  if(active){
    const pulse = 0.55 + Math.sin(Date.now()/220)*0.25;
    let grad = ctx.createRadialGradient(g.x+g.w/2,g.y+g.h/2,4,g.x+g.w/2,g.y+g.h/2,g.w);
    grad.addColorStop(0, `rgba(6,182,212,${pulse})`);
    grad.addColorStop(1, 'rgba(124,58,237,0)');
    ctx.fillStyle = grad;
    ctx.beginPath(); ctx.arc(g.x+g.w/2,g.y+g.h/2,g.w*0.9,0,7); ctx.fill();
    ctx.strokeStyle = `rgba(165,243,252,${pulse+0.2})`;
    ctx.lineWidth = 3;
    ctx.strokeRect(g.x,g.y,g.w,g.h);
    ctx.fillStyle = '#e0f2fe';
    ctx.font = '11px Outfit';
    ctx.textAlign = 'center';
    ctx.fillText('JUMP', g.x+g.w/2, g.y-8);
  } else {
    // locked / inactive portal outline
    ctx.strokeStyle = 'rgba(150,150,170,0.35)';
    ctx.lineWidth = 2;
    ctx.setLineDash([4,4]);
    ctx.strokeRect(g.x,g.y,g.w,g.h);
    ctx.setLineDash([]);
    ctx.fillStyle = 'rgba(200,200,220,0.5)';
    ctx.font = '10px Outfit';
    ctx.textAlign = 'center';
    ctx.fillText('LOCKED', g.x+g.w/2, g.y-8);
  }
  ctx.restore();
}

function draw(){
  ctx.clearRect(0,0,W,H);
  ctx.save();
  if(camShake>0){ ctx.translate((Math.random()-0.5)*camShake,(Math.random()-0.5)*camShake); }

  ctx.fillStyle = 'rgba(255,255,255,0.04)';
  for(let i=0;i<5;i++){ ctx.fillRect(60+i*180, 60, 40, 380); }
  ctx.fillStyle = 'rgba(124,58,237,0.08)';
  ctx.beginPath(); ctx.arc(150,90,50,0,7); ctx.fill();

  for(const p of level.platforms){
    let grad = ctx.createLinearGradient(p.x,p.y,p.x,p.y+p.h);
    grad.addColorStop(0,'#4a2a6a'); grad.addColorStop(1,'#241040');
    ctx.fillStyle = grad;
    ctx.fillRect(p.x,p.y,p.w,p.h);
    ctx.strokeStyle='rgba(255,255,255,0.08)';
    ctx.strokeRect(p.x,p.y,p.w,p.h);
  }

  for(const s of level.scrolls){
    if(s.taken) continue;
    ctx.save();
    ctx.translate(s.x+10, s.y+10+Math.sin(Date.now()/300+s.x)*4);
    ctx.fillStyle='#ffd700';
    ctx.fillRect(-8,-6,16,12);
    ctx.fillStyle='#7c3aed';
    ctx.fillRect(-8,-8,16,3);
    ctx.restore();
  }

  if(level.type==='normal'){
    drawGoal(level.goal, true);
    for(const e of level.enemies) drawEnemy(e);
  } else {
    drawGoal(level.goal, level.bossDefeated);
    drawBoss();
  }

  drawPlayer();

  for(const f of fireballs){
    let grad = ctx.createRadialGradient(f.x,f.y,0,f.x,f.y,10);
    grad.addColorStop(0,'#fff2b0'); grad.addColorStop(0.5,'#ff9d00'); grad.addColorStop(1,'rgba(255,77,0,0)');
    ctx.fillStyle=grad;
    ctx.beginPath(); ctx.arc(f.x,f.y,10,0,7); ctx.fill();
  }
  for(const pr of projectiles){
    ctx.fillStyle = pr.fire ? '#ff9d00' : (pr.ground ? '#c4c4c4' : '#ff4d6d');
    ctx.beginPath(); ctx.arc(pr.x,pr.y,pr.ground?5:4,0,7); ctx.fill();
  }
  for(const p of particles){
    ctx.globalAlpha = Math.max(0,p.life/40);
    ctx.fillStyle = p.color;
    ctx.fillRect(p.x,p.y,4,4);
    ctx.globalAlpha=1;
  }

  ctx.restore();
}

function loop(){
  update();
  draw();
  requestAnimationFrame(loop);
}
loop();
</script>
</body>
</html>
"""

components.html(GAME_HTML, height=620, scrolling=False)

st.markdown("""
<div style="text-align:center; color:#7c6a9e; font-size:13px; margin-top:6px;">
🥷 6 normal levels + 5 boss fights: Temple Guardian, Shadow Assassin, Stone Golem, Phoenix Sentinel, Dragon Emperor
</div>
""", unsafe_allow_html=True)
