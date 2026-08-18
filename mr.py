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
.title-wrap {
    text-align: center;
    padding: 8px 0 4px 0;
}
.title-wrap h1 {
    background: linear-gradient(90deg, #ff4d4d, #ff9d00, #7c3aed, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    font-size: 2.6rem;
    margin-bottom: 0;
    letter-spacing: 1px;
}
.subtitle {
    text-align: center;
    color: #a78bfa;
    font-weight: 300;
    margin-top: -8px;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="title-wrap"><h1>🐉 DRAGON NINJA 🥷</h1></div>
<div class="subtitle">Slash. Dash. Breathe fire. Survive the temple.</div>
""", unsafe_allow_html=True)

GAME_HTML = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * { box-sizing: border-box; margin:0; padding:0; }
  body {
    font-family: 'Outfit', sans-serif;
    display:flex; flex-direction:column; align-items:center;
    background: transparent;
  }
  #gameWrap {
    position: relative;
    width: 900px;
    max-width: 100%;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 0 40px rgba(124,58,237,0.35), 0 0 0 1px rgba(255,255,255,0.08);
  }
  canvas {
    display:block;
    width: 100%;
    background: linear-gradient(180deg,#150a2e 0%, #2a1450 55%, #3d1a4a 100%);
  }
  #hud {
    position:absolute; top:10px; left:10px; right:10px;
    display:flex; justify-content:space-between; align-items:flex-start;
    pointer-events:none; color:#fff; font-family:'Outfit',sans-serif;
  }
  .panel {
    background: rgba(10,5,25,0.55);
    backdrop-filter: blur(6px);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 10px;
    padding: 8px 12px;
    font-size: 13px;
  }
  .barBg {
    width: 160px; height: 12px; border-radius:6px;
    background: rgba(255,255,255,0.1);
    overflow:hidden; margin-top:4px;
  }
  .barFill { height:100%; border-radius:6px; transition: width 0.15s; }
  #hpFill { background: linear-gradient(90deg,#ff4d6d,#ff9d00); }
  #chiFill { background: linear-gradient(90deg,#06b6d4,#7c3aed); }
  #overlay {
    position:absolute; inset:0;
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    background: rgba(5,2,15,0.82);
    color:#fff; text-align:center; gap:10px;
  }
  #overlay h2 { font-size:32px; background: linear-gradient(90deg,#ff4d4d,#ff9d00,#7c3aed);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
  #overlay p { color:#c4b5fd; max-width:480px; font-size:14px; line-height:1.5; }
  button.gbtn {
    margin-top:8px;
    background: linear-gradient(90deg,#7c3aed,#06b6d4);
    border:none; color:#fff; padding:10px 24px; border-radius:24px;
    font-size:15px; font-weight:600; cursor:pointer; font-family:'Outfit',sans-serif;
  }
  button.gbtn:hover { filter: brightness(1.15); }
  #controls {
    margin-top:10px; color:#a78bfa; font-size:12.5px; text-align:center; line-height:1.6;
  }
  #controls b { color:#e9d5ff; }
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
      <div>Level <span id="lvl">1</span> — Scrolls: <span id="scrolls">0</span>/<span id="scrollsTotal">5</span></div>
      <div style="margin-top:2px;">🔥 Chi</div>
      <div class="barBg"><div class="barFill" id="chiFill" style="width:100%"></div></div>
    </div>
  </div>
  <div id="overlay">
    <h2>🐉 DRAGON NINJA 🥷</h2>
    <p>You are the last Dragon Ninja. Collect the ancient scrolls, cut down shadow warriors,
       and defeat the Temple Guardian using steel and fire.</p>
    <div id="controls">
      <b>← → / A D</b> Move &nbsp;•&nbsp; <b>SPACE / W</b> Jump (double-jump!) &nbsp;•&nbsp; <b>J</b> Sword Slash<br>
      <b>K</b> Fire Breath (uses Chi) &nbsp;•&nbsp; <b>SHIFT</b> Dash &nbsp;•&nbsp; Hold direction near wall to slide down slower
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
// Each level: platforms, enemies, scrolls, goal (boss on last level)
function buildLevels(){
  return [
    {
      platforms: [
        {x:0,y:460,w:900,h:40}, {x:150,y:370,w:120,h:20}, {x:340,y:300,w:120,h:20},
        {x:540,y:250,w:120,h:20}, {x:700,y:380,w:150,h:20}, {x:60,y:250,w:100,h:20}
      ],
      enemies: [
        {x:400,y:270,w:34,h:40,vx:1.4,range:[340,460],hp:2,type:'shadow'},
        {x:750,y:350,w:34,h:40,vx:1.2,range:[700,840],hp:2,type:'shadow'}
      ],
      scrolls: [{x:190,y:335,taken:false},{x:600,y:215,taken:false},{x:90,y:215,taken:false}],
      spawn:{x:30,y:400}, goalX: 860, boss:false
    },
    {
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
      scrolls: [{x:250,y:185,taken:false},{x:540,y:125,taken:false},{x:800,y:365,taken:false},{x:460,y:245,taken:false}],
      spawn:{x:30,y:400}, goalX: 860, boss:false
    },
    {
      platforms: [
        {x:0,y:460,w:900,h:40}, {x:0,y:460,w:200,h:40},
        {x:250,y:420,w:400,h:20}, {x:700,y:460,w:200,h:40}
      ],
      enemies: [],
      scrolls: [{x:100,y:390,taken:false}],
      spawn:{x:50,y:400}, goalX: 0, boss:true
    }
  ];
}

let levels = buildLevels();
let levelIdx = 0;
let level = levels[0];

// ---------- Player ----------
const player = {
  x:30,y:400,w:34,h:44,vx:0,vy:0,
  onGround:false, facing:1, hp:100, maxHp:100, chi:100, maxChi:100,
  jumps:0, maxJumps:2, dashCd:0, slashCd:0, breathCd:0,
  slashTimer:0, invuln:0, breathTimer:0
};

let particles = [];
let projectiles = []; // enemy arrows
let fireballs = []; // player breath particles
let scrollsCollected = 0;
let gameState = 'menu'; // menu, playing, dead, win, levelclear
let bossHp = 60, bossMaxHp = 60, bossPhase=1, bossTimer=0, bossX=650, bossY=380, bossVx=-1.5, bossAttackCd=0;
let camShake = 0;

function resetLevel(idx){
  level = JSON.parse(JSON.stringify(levels[idx]));
  player.x = level.spawn.x; player.y = level.spawn.y;
  player.vx=0; player.vy=0; player.jumps=0; player.invuln=60;
  projectiles = []; fireballs = []; particles=[];
  if(level.boss){ bossHp=60; bossMaxHp=60; bossX=650; bossY=380; bossVx=-1.5; bossAttackCd=90; bossPhase=1; }
  document.getElementById('lvl').innerText = idx+1;
  document.getElementById('scrollsTotal').innerText = level.scrolls.length;
  document.getElementById('scrolls').innerText = '0';
}

function startGame(){
  levelIdx = 0;
  player.hp = player.maxHp; player.chi = player.maxChi;
  scrollsCollected = 0;
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

function update(){
  if(gameState !== 'playing') return;

  // --- input / movement ---
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

  if(keys['j'] && player.slashCd<=0){
    player.slashCd = 22; player.slashTimer = 10;
  }
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

  // --- enemies ---
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
    // slash hits
    if(player.slashTimer>0){
      const reach = {x: player.facing>0?player.x+player.w:player.x-30, y:player.y, w:30, h:player.h};
      if(rectsOverlap(reach,e)){
        e.hp -= 1;
        spawnParticles(e.x+e.w/2,e.y+e.h/2,'#ff9d00',6,4);
        e._hitCd = 10;
      }
    }
    // contact damage from shadow already above; archer contact:
    if(rectsOverlap(player,e) && player.invuln<=0){
      player.hp -= 8; player.invuln=45; camShake=8;
    }
  }

  // fireballs vs enemies
  for(const fb of fireballs){
    fb.x += fb.vx; fb.y += fb.vy; fb.life--;
    for(const e of level.enemies){
      if(e.hp>0 && rectsOverlap({x:fb.x-8,y:fb.y-8,w:16,h:16}, e)){
        e.hp -= 2; fb.life=0;
        spawnParticles(e.x+e.w/2,e.y+e.h/2,'#ff6b00',10,5);
      }
    }
    if(level.boss && bossHp>0 && rectsOverlap({x:fb.x-8,y:fb.y-8,w:16,h:16},{x:bossX,y:bossY,w:70,h:80})){
      bossHp -= 3; fb.life=0;
      spawnParticles(bossX+35,bossY+40,'#ff6b00',10,5);
    }
  }
  fireballs = fireballs.filter(f=>f.life>0);

  // enemy projectiles
  for(const pr of projectiles){
    pr.x += pr.vx; pr.life--;
    if(rectsOverlap({x:pr.x-4,y:pr.y-4,w:8,h:8}, player) && player.invuln<=0){
      player.hp -= 10; player.invuln=40; pr.life=0; camShake=8;
    }
  }
  projectiles = projectiles.filter(p=>p.life>0);

  // scrolls
  for(const s of level.scrolls){
    if(!s.taken && rectsOverlap({x:s.x,y:s.y,w:20,h:20}, player)){
      s.taken = true; scrollsCollected++;
      document.getElementById('scrolls').innerText = level.scrolls.filter(x=>x.taken).length;
      spawnParticles(s.x+10,s.y+10,'#ffd700',14,5);
    }
  }

  // particles
  for(const p of particles){ p.x+=p.vx; p.y+=p.vy; p.vy+=0.15; p.life--; }
  particles = particles.filter(p=>p.life>0);

  // boss logic
  if(level.boss && gameState==='playing'){
    bossAttackCd--;
    let dx = (player.x - bossX);
    if(Math.abs(dx)>60) bossX += Math.sign(dx)*1.6*(bossPhase);
    bossX = Math.max(20, Math.min(W-90, bossX));
    if(bossAttackCd<=0){
      bossAttackCd = bossPhase===1?80:50;
      // slam ground - spawn 3 projectiles fan
      for(let a=-1;a<=1;a++){
        projectiles.push({x:bossX+35,y:bossY+20,vx:a*4 + (player.x>bossX?2:-2),vy:-6,life:200,grav:true});
      }
    }
    if(bossHp <= bossMaxHp/2) bossPhase = 2;
    if(rectsOverlap(player,{x:bossX,y:bossY,w:70,h:80}) && player.invuln<=0){
      player.hp -= 12; player.invuln = 40; camShake=10;
    }
    if(player.slashTimer>0){
      const reach = {x: player.facing>0?player.x+player.w:player.x-30, y:player.y, w:30, h:player.h};
      if(rectsOverlap(reach,{x:bossX,y:bossY,w:70,h:80})){
        bossHp -= 0.6;
        spawnParticles(bossX+35,bossY+40,'#ff9d00',4,4);
      }
    }
    if(bossHp<=0){
      gameState='win';
      showOverlay('🐉 VICTORY!', 'You defeated the Temple Guardian and restored balance to the Dragon Temple. Total scrolls collected: '+scrollsCollected, 'Play Again');
    }
  }

  // gravity projectiles (boss)
  for(const pr of projectiles){ if(pr.grav){ pr.vy += 0.25; pr.x+=pr.vx; pr.y+=pr.vy; } }

  // win condition non-boss levels
  if(!level.boss && player.x > level.goalX){
    gameState='levelclear';
    let allScrolls = level.scrolls.filter(s=>s.taken).length === level.scrolls.length;
    showOverlay('Level Complete!', allScrolls? 'All scrolls collected! Bonus chi restored.' : 'Gate reached. Some scrolls remain hidden in the shadows.', 'Continue');
    if(allScrolls) player.chi = player.maxChi;
  }

  if(player.hp<=0){
    gameState='dead';
    showOverlay('💀 You Have Fallen', 'The shadow warriors overwhelmed you. Total scrolls collected: '+scrollsCollected, 'Retry Level');
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
      if(levelIdx>=levels.length){ startGame(); return; }
      resetLevel(levelIdx); gameState='playing'; ov.style.display='none';
    } else if(gameState==='win'){ startGame(); }
  });
}

// ---------- Draw ----------
function drawPlayer(){
  ctx.save();
  let sx = player.x+player.w/2, sy=player.y+player.h/2;
  ctx.translate(sx,sy);
  ctx.scale(player.facing,1);
  ctx.translate(-player.w/2,-player.h/2);
  // cloak glow if invulnerable
  if(player.invuln>0 && Math.floor(player.invuln/4)%2===0){
    ctx.globalAlpha = 0.5;
  }
  // body
  ctx.fillStyle = '#1e1030';
  ctx.fillRect(4,10,player.w-8,player.h-14);
  // dragon-scale trim
  ctx.fillStyle = '#7c3aed';
  ctx.fillRect(4,10,player.w-8,6);
  // head
  ctx.fillStyle = '#2a1a40';
  ctx.fillRect(6,0,player.w-12,14);
  // eye glow
  ctx.fillStyle = '#ff9d00';
  ctx.fillRect(player.w-14,5,4,3);
  // legs
  ctx.fillStyle = '#150a20';
  ctx.fillRect(6,player.h-10,8,10);
  ctx.fillRect(player.w-14,player.h-10,8,10);
  // sword slash
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
  // hp pips
  for(let i=0;i<e.hp;i++){
    ctx.fillStyle='#ff4d6d';
    ctx.fillRect(e.x+i*8, e.y-8, 6,4);
  }
  ctx.restore();
}

function drawBoss(){
  if(!level.boss) return;
  ctx.save();
  ctx.fillStyle = '#3a0d0d';
  ctx.fillRect(bossX,bossY,70,80);
  ctx.fillStyle = '#ff4d4d';
  ctx.fillRect(bossX+50,bossY+10,10,8);
  ctx.fillRect(bossX+10,bossY+10,10,8);
  ctx.fillStyle='#ff9d00';
  ctx.fillRect(bossX+15,bossY+15,6,4);
  ctx.fillRect(bossX+49,bossY+15,6,4);
  ctx.restore();
  // boss hp bar
  ctx.fillStyle = 'rgba(255,255,255,0.15)';
  ctx.fillRect(W/2-150,20,300,14);
  ctx.fillStyle = '#ff4d6d';
  ctx.fillRect(W/2-150,20,300*Math.max(0,bossHp/bossMaxHp),14);
  ctx.strokeStyle='rgba(255,255,255,0.4)';
  ctx.strokeRect(W/2-150,20,300,14);
  ctx.fillStyle='#fff'; ctx.font='12px Outfit'; ctx.textAlign='center';
  ctx.fillText('Temple Guardian', W/2, 16);
}

function draw(){
  ctx.clearRect(0,0,W,H);
  ctx.save();
  if(camShake>0){ ctx.translate((Math.random()-0.5)*camShake,(Math.random()-0.5)*camShake); }

  // bg temple silhouettes
  ctx.fillStyle = 'rgba(255,255,255,0.04)';
  for(let i=0;i<5;i++){ ctx.fillRect(60+i*180, 60, 40, 380); }
  ctx.fillStyle = 'rgba(124,58,237,0.08)';
  ctx.beginPath(); ctx.arc(150,90,50,0,7); ctx.fill();

  // platforms
  for(const p of level.platforms){
    let grad = ctx.createLinearGradient(p.x,p.y,p.x,p.y+p.h);
    grad.addColorStop(0,'#4a2a6a'); grad.addColorStop(1,'#241040');
    ctx.fillStyle = grad;
    ctx.fillRect(p.x,p.y,p.w,p.h);
    ctx.strokeStyle='rgba(255,255,255,0.08)';
    ctx.strokeRect(p.x,p.y,p.w,p.h);
  }

  // scrolls
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

  // goal marker
  if(!level.boss){
    ctx.fillStyle='rgba(6,182,212,0.35)';
    ctx.fillRect(level.goalX,0,4,H);
  }

  for(const e of level.enemies) drawEnemy(e);
  drawBoss();
  drawPlayer();

  // fireballs
  for(const f of fireballs){
    let grad = ctx.createRadialGradient(f.x,f.y,0,f.x,f.y,10);
    grad.addColorStop(0,'#fff2b0'); grad.addColorStop(0.5,'#ff9d00'); grad.addColorStop(1,'rgba(255,77,0,0)');
    ctx.fillStyle=grad;
    ctx.beginPath(); ctx.arc(f.x,f.y,10,0,7); ctx.fill();
  }
  // enemy projectiles
  for(const pr of projectiles){
    ctx.fillStyle='#ff4d6d';
    ctx.beginPath(); ctx.arc(pr.x,pr.y,4,0,7); ctx.fill();
  }
  // particles
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
🥷 Move with A/D or arrows • Double-jump with Space • J to slash • K to breathe fire (uses chi) • Shift to dash through enemies
</div>
""", unsafe_allow_html=True)
