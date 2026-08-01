import Alpine from 'alpinejs';
import DOMPurify from 'dompurify';
import { marked } from 'marked';

type Preset = {
  id: string;
  name: string;
  emoji: string;
  radius: string;
  styles: string;
};

const allowedTags = [
  'a',
  'del',
  'p',
  'br',
  'strong',
  'em',
  'code',
  'pre',
  'ul',
  'ol',
  'li',
  'h1',
  'h2',
  'h3',
  'h4',
  'h5',
  'h6',
  'hr',
  'img',
];

const allowedImgDomains = ['.giphy.com', '.tenor.com', '.ibb.co'];
const allowedAttrs = ['src', 'alt', 'height', 'width'];

DOMPurify.addHook('uponSanitizeAttribute', (node, data) => {
  const tag = node.nodeName.toLowerCase();

  if (tag === 'img') {
    if (!allowedAttrs.includes(data.attrName)) {
      data.keepAttr = false;
      return;
    }

    if (data.attrName === 'src' && !isValidImgSrc(data.attrValue)) {
      data.keepAttr = false;
    }
  } else {
    data.keepAttr = false;
  }
});

function isValidImgSrc(value: string): boolean {
  try {
    const url = new URL(value, 'https://placeholder');
    const hostname = url.hostname;
    return !hostname || allowedImgDomains.some(d => hostname.endsWith(d));
  } catch {
    return false;
  }
}

function getPresets() {
  const dataElm = document.getElementById('guestbook-editor-presets');
  const raw = dataElm?.textContent;

  try {
    if (!raw) throw new Error('No preset data found');

    const presets = JSON.parse(raw) as Preset[];

    if (!Array.isArray(presets)) {
      throw new Error('Invalid preset format');
    }

    return presets;
  } catch (err) {
    console.error('Failed to parse presets:', err);
    return [];
  }
}

Alpine.data('guestbookEditor', () => {
  const presets: Preset[] = getPresets();
  const initialPreset = presets[0] ?? {};

  return {
    init() {
      this.updatePreviewMessage();

      this.$watch('form.message', () => {
        this.updatePreviewMessage();
      });
    },

    isPreviewVisible: true,

    form: {
      name: '',
      message: '',
      url: '',
      radius: initialPreset.radius ?? '',
      emoji: initialPreset.emoji ?? '',
      style: initialPreset.id ?? '',
    },

    get activePreset() {
      return presets.find(p => p.id === this.form.style) ?? initialPreset;
    },

    get previewCardClasses(): string {
      const styles = this.activePreset?.styles ?? '';
      const radius = this.form.radius || this.activePreset?.radius || '';

      return `${styles} ${radius}`.trim();
    },

    get formattedName() {
      return `— ${this.form.name}`;
    },

    get previewToggleIconClass() {
      return this.isPreviewVisible ? 'rotate-180' : '';
    },

    get canShowNameWithUrl() {
      return this.form.name && this.form.url;
    },

    get canShowNameOnly() {
      return this.form.name && !this.form.url;
    },

    get isTargetSelected(): boolean {
      const elm = this.$el as HTMLInputElement | HTMLOptionElement;
      const name = elm.getAttribute('name');

      return !!name && elm.value === this.form[name as keyof typeof this.form];
    },

    updateFormField(event: Event) {
      const target = event.target as HTMLInputElement;
      const key = target.name as keyof typeof this.form | null;

      if (!key || !(key in this.form)) return;

      this.form[key] = target.value;
    },

    togglePreviewVisibility() {
      this.isPreviewVisible = !this.isPreviewVisible;
    },

    async updatePreviewMessage() {
      const previewMessage = this.$refs.previewMessage as HTMLElement | undefined;
      if (!previewMessage) return;

      if (!this.form.message) {
        previewMessage.textContent = 'Your message will appear here';
        return;
      }

      previewMessage.innerHTML = await this.renderMarkdown(this.form.message);
    },

    async renderMarkdown(md: string = '') {
      const rawHtml = await marked.parse(md);

      return DOMPurify.sanitize(rawHtml, {
        ALLOWED_TAGS: allowedTags,
        ALLOWED_ATTR: allowedAttrs,
      });
    },
  };
});
