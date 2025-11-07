// Ensure favicon is set to GRP Spallenta across Desk
(function setGRPFavicon() {
  try {
    const head = document.head || document.getElementsByTagName('head')[0];

    const removeExisting = () => {
      [...head.querySelectorAll('link[rel="icon"], link[rel="shortcut icon"], link[rel="apple-touch-icon"]')].forEach((el) => el.parentNode.removeChild(el));
    };

    const add = (rel, href, type, sizes) => {
      const link = document.createElement('link');
      link.rel = rel;
      link.href = href;
      if (type) link.type = type;
      if (sizes) link.sizes = sizes;
      head.appendChild(link);
    };

    const base = '/assets/lending/images';
    removeExisting();

    // Standard favicons
    add('icon', `${base}/favicon.ico`, 'image/x-icon');
    add('icon', `${base}/favicon-32.png`, 'image/png', '32x32');
    add('icon', `${base}/favicon-16.png`, 'image/png', '16x16');

    // Apple touch icon
    add('apple-touch-icon', `${base}/apple-touch-icon.png`, undefined, '180x180');

    // Maskable/manifest optional
    // add('manifest', `${base}/site.webmanifest`);
  } catch (e) {
    // Fail silently
  }
})();
