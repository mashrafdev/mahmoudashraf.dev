import Alpine from 'alpinejs';

Alpine.data('headerNav', () => ({
  open: false,

  init() {
    // The desktop nav takes over at Tailwind's `sm` breakpoint; reset the mobile state there.
    const desktop = window.matchMedia('(min-width: 40rem)');

    desktop.addEventListener('change', event => {
      if (event.matches) {
        this.open = false;
      }
    });
  },

  get openStr() {
    return this.open ? 'true' : 'false';
  },

  get opened() {
    return this.open;
  },

  get closed() {
    return !this.open;
  },

  toggle() {
    this.open = !this.open;
  },

  close() {
    this.open = false;
  },

  closeAndFocus() {
    if (!this.open) return;

    // Escape should only return focus if it was inside the menu, not from elsewhere on the page.
    const focusIsInMenu = this.$refs.mobileMenu?.contains(document.activeElement);

    this.open = false;

    if (focusIsInMenu) {
      this.$refs.menuButton?.focus();
    }
  },
}));
