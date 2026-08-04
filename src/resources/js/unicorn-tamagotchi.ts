import Alpine from 'alpinejs';

interface Stage {
  minClicks: number;
  emoji: string;
  particles: string[];
  quotes: string[];
  glowClass: string;
}

interface Combo {
  minCombo: number;
  sound: 'combo_low' | 'combo_mid' | 'combo_high' | 'combo_god';
  quote: string;
  burstParticles: string[];
}

const STAGES: Stage[] = [
  {
    minClicks: 0,
    emoji: '🥚',
    particles: ['✨', '💤', '🌱'],
    quotes: ['[0x00] init', 'python manage.py egg', '*hatching...*'],
    glowClass: 'drop-shadow-[0_0_6px_#c7f800]',
  },
  {
    minClicks: 10,
    emoji: '🐣',
    particles: ['✨', '🌱', '🐣'],
    quotes: ['*cracking!*', 'Django Powered! 🐍', 'git commit -m "hatch"'],
    glowClass: 'drop-shadow-[0_0_8px_#c7f800]',
  },
  {
    minClicks: 20,
    emoji: '🐥',
    particles: ['🐥', '🐤', '⚡', '🚀', '🔥'],
    quotes: ['Status 200 OK! ⚡', 'Chirp chirp! ☕', 'Ship it! 🚀'],
    glowClass: 'drop-shadow-[0_0_10px_#16a085] scale-105',
  },
  {
    minClicks: 50,
    emoji: '🐎',
    particles: ['🐎', '💨', '🎉', '💎'],
    quotes: ['Root Access Granted! 👑', 'ALL TESTS PASSED! 🏆', 'Giddy up!'],
    glowClass: 'drop-shadow-[0_0_14px_#e5ff53] scale-110',
  },
  {
    minClicks: 100,
    emoji: '🦄',
    particles: ['🦄', '💖', '✨', '⭐', '🌸'],
    quotes: ['*neigh!*', 'Magic unlocked! 💖', 'Unicorn power! 🦄'],
    glowClass: 'drop-shadow-[0_0_20px_#ff00ff] scale-125',
  },
];

const COMBOS: Combo[] = [
  {
    minCombo: 10,
    sound: 'combo_low',
    quote: '⚡ {count}x SPEED!',
    burstParticles: ['⚡', '✨'],
  },
  {
    minCombo: 20,
    sound: 'combo_mid',
    quote: '🔥 {count}x MULTI-BOOP!',
    burstParticles: ['🔥', '💥', '⚡'],
  },
  {
    minCombo: 50,
    sound: 'combo_high',
    quote: '🚀 {count}x TURBO MODE!',
    burstParticles: ['🚀', '🌟', '💥', '⚡'],
  },
  {
    minCombo: 100,
    sound: 'combo_god',
    quote: '🌌 {count}x GOD TIER STREAK!',
    burstParticles: ['🌌', '🎆', '👑', '⚡', '💥', '🦄'],
  },
];

Alpine.data('unicornTamagotchi', () => ({
  clicks: 0,
  animating: false,
  statusMessage: '',
  showStatus: false,
  statusTimeout: null as any,
  comboCount: 0,
  comboTimer: null as any,
  audioCtx: null as AudioContext | null,

  init() {
    this.clicks = 0;
  },

  playSound(
    type: 'boop' | 'combo_low' | 'combo_mid' | 'combo_high' | 'combo_god' | 'evolve' | 'win',
  ) {
    try {
      if (!this.audioCtx) {
        const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
        this.audioCtx = new AudioContextClass();
      }

      if (this.audioCtx.state === 'suspended') {
        this.audioCtx.resume();
      }

      const ctx = this.audioCtx;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      const now = ctx.currentTime;

      if (type === 'boop') {
        osc.type = 'sine';
        osc.frequency.setValueAtTime(380 + Math.random() * 120, now);
        osc.frequency.exponentialRampToValueAtTime(760, now + 0.08);
        gain.gain.setValueAtTime(0.1, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.08);
        osc.start(now);
        osc.stop(now + 0.08);
      } else if (type === 'combo_low') {
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(523.25, now);
        osc.frequency.setValueAtTime(659.25, now + 0.05);
        gain.gain.setValueAtTime(0.1, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.15);
        osc.start(now);
        osc.stop(now + 0.15);
      } else if (type === 'combo_mid') {
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(523.25, now);
        osc.frequency.setValueAtTime(659.25, now + 0.04);
        osc.frequency.setValueAtTime(783.99, now + 0.08);
        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.2);
        osc.start(now);
        osc.stop(now + 0.2);
      } else if (type === 'combo_high') {
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(400, now);
        osc.frequency.exponentialRampToValueAtTime(1400, now + 0.15);
        gain.gain.setValueAtTime(0.1, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.2);
        osc.start(now);
        osc.stop(now + 0.2);
      } else if (type === 'combo_god') {
        osc.type = 'square';
        [523.25, 659.25, 783.99, 1046.5, 1318.5, 1567.98].forEach((freq, idx) => {
          osc.frequency.setValueAtTime(freq, now + idx * 0.03);
        });
        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
        osc.start(now);
        osc.stop(now + 0.35);
      } else if (type === 'evolve') {
        osc.type = 'square';
        [300, 450, 600, 900].forEach((freq, idx) => {
          osc.frequency.setValueAtTime(freq, now + idx * 0.06);
        });
        gain.gain.setValueAtTime(0.08, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
        osc.start(now);
        osc.stop(now + 0.35);
      } else if (type === 'win') {
        osc.type = 'triangle';
        [523.25, 659.25, 783.99, 1046.5].forEach((freq, i) => {
          osc.frequency.setValueAtTime(freq, now + i * 0.12);
        });
        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.6);
        osc.start(now);
        osc.stop(now + 0.6);
      }
    } catch (e) {
      console.error(e);
    }
  },

  spawnParticle(overrideEmoji?: string) {
    const container = this.$refs.particleContainer as HTMLElement;
    if (!container) return;

    const emojis = overrideEmoji ? [overrideEmoji] : this.currentStage.particles;
    const text = emojis[Math.floor(Math.random() * emojis.length)];

    const el = document.createElement('span');
    el.textContent = text;
    el.className =
      'absolute pointer-events-none text-xs select-none z-50 transition-all duration-700 ease-out font-mono';

    const x = (Math.random() - 0.5) * 40;
    const y = -30 - Math.random() * 25;

    el.style.left = '50%';
    el.style.bottom = '100%';
    el.style.transform = `translate(${x}px, 0px) scale(0.6)`;
    el.style.opacity = '1';

    container.appendChild(el);

    requestAnimationFrame(() => {
      el.style.transform = `translate(${x * 1.5}px, ${y}px) scale(1.3) rotate(${(Math.random() - 0.5) * 50}deg)`;
      el.style.opacity = '0';
    });

    setTimeout(() => el.remove(), 700);
  },

  tap() {
    const oldStageIndex = this.stageIndex;
    this.clicks++;

    this.animating = true;
    setTimeout(() => {
      this.animating = false;
    }, 300);

    // Combo tracking
    this.comboCount++;
    clearTimeout(this.comboTimer);
    this.comboTimer = setTimeout(() => {
      this.comboCount = 0;
    }, 1000);

    const activeCombo = this.currentCombo;

    this.spawnParticle();
    if (activeCombo) {
      activeCombo.burstParticles.forEach(p => this.spawnParticle(p));
    }

    const newStageIndex = this.stageIndex;

    if (newStageIndex > oldStageIndex) {
      if (newStageIndex === STAGES.length - 1) {
        this.playSound('win');
        this.triggerStatus('🏆 MAX LEVEL UNLOCKED!');
      } else {
        this.playSound('evolve');
        this.triggerStatus('✨ SYSTEM EVOLVED!');
      }
    } else if (activeCombo) {
      this.playSound(activeCombo.sound);
      this.triggerStatus(activeCombo.quote.replace('{count}', this.comboCount.toString()));
    } else {
      this.playSound('boop');
      this.triggerStatus(this.randomQuote);
    }
  },

  triggerStatus(text: string) {
    this.statusMessage = text;
    this.showStatus = true;
    clearTimeout(this.statusTimeout);
    this.statusTimeout = setTimeout(() => {
      this.showStatus = false;
    }, 1300);
  },

  get stageIndex(): number {
    for (let i = STAGES.length - 1; i >= 0; i--) {
      if (this.clicks >= STAGES[i].minClicks) return i;
    }
    return 0;
  },

  get currentStage(): Stage {
    return STAGES[this.stageIndex];
  },

  get currentCombo(): Combo | null {
    for (let i = COMBOS.length - 1; i >= 0; i--) {
      if (this.comboCount >= COMBOS[i].minCombo) return COMBOS[i];
    }
    return null;
  },

  get emoji(): string {
    return this.currentStage.emoji;
  },

  get randomQuote(): string {
    const quotes = this.currentStage.quotes;
    return quotes[Math.floor(Math.random() * quotes.length)];
  },

  get statusText(): string {
    return this.statusMessage;
  },

  get buttonClasses(): string {
    let classes =
      'inline-block ml-1 select-none transition-all duration-300 transform outline-none cursor-pointer ';
    if (this.animating) {
      classes += ' -translate-y-2 scale-125 rotate-12 ';
    }
    classes += ` ${this.currentStage.glowClass} `;
    return classes;
  },
}));
