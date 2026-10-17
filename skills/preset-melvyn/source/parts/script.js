      const tl = gsap.timeline({ paused: true });
      // courbes douces : entrées expo.out ~0,7 s, sorties courtes power2.in
      const IN = "expo.out", D = 0.7;
      const rise = (sel, t, extra = {}) => tl.fromTo(sel, { opacity: 0, y: 28 }, { opacity: 1, y: 0, duration: D, ease: IN, ...extra }, t);
      const pop = (sel, t, extra = {}) => tl.fromTo(sel, { opacity: 0, scale: 0.92 }, { opacity: 1, scale: 1, duration: D, ease: IN, ...extra }, t);
      const out = (sel, t, extra = {}) => tl.to(sel, { opacity: 0, duration: 0.3, ease: "power2.in", ...extra }, t);
      const draw = (sel, t, d = 0.6, prop = "scaleX") => tl.fromTo(sel, { [prop]: 0 }, { [prop]: 1, duration: d, ease: "expo.inOut" }, t);

      // fondus de section : la scène s'efface, la suivante entre sur le papier
      const SC = [["#s0", 0, 3.06], ["#s1", 3.06, 6.58], ["#s2", 6.58, 10.54], ["#s3", 10.54, 13.70], ["#s4", 13.70, 15.84], ["#s5", 15.84, 20.06], ["#s6", 20.06, 24.36], ["#s7", 24.36, 27.48], ["#s8", 27.48, 31.267]];
      SC.forEach(([s, a, b], i) => {
        if (i > 0) tl.fromTo(s + " > .in", { opacity: 0 }, { opacity: 1, duration: 0.3, ease: "power1.out" }, a);
        if (i < SC.length - 1) tl.to(s + " > .in", { opacity: 0, duration: 0.28, ease: "power2.in" }, b - 0.28);
      });
      // en-têtes d'étape
      ["#s2", "#s3", "#s4", "#s5", "#s6"].forEach((s, i) => rise(s + " .head .pill", [6.58, 10.54, 13.70, 15.84, 20.06][i] + 0.05));

      // s0 — bouton « Publier » : le curseur arrive, clic, tampon « pas encore », puis le 5
      rise("#s0btn", 0.05);
      tl.fromTo("#s0cur", { opacity: 0, x: 140, y: 120 }, { opacity: 1, x: 0, y: 0, duration: 0.6, ease: "expo.out" }, 0.1);
      tl.to("#s0cur", { x: -110, y: -150, duration: 0.5, ease: "power3.inOut" }, 0.62);
      tl.to("#s0btn", { scale: 0.95, duration: 0.08, ease: "power2.out" }, 1.1).to("#s0btn", { scale: 1, duration: 0.3, ease: IN }, 1.18);
      tl.fromTo("#s0stamp", { opacity: 0, scale: 1.25 }, { opacity: 1, scale: 1, duration: 0.45, ease: IN }, 1.3);
      out(["#s0btn", "#s0stamp", "#s0cur"], 1.66);
      pop("#s0five", 1.96, { duration: 0.8 });
      rise("#s0pill", 2.70);

      // s1 — dépôt GitHub + « gratuit », puis Venn Claude ∩ équipe vidéo
      rise("#s1repo", 3.12);
      pop("#s1free", 3.44, { rotation: 5 });
      out("#s1repo", 4.12);
      tl.fromTo("#s1L", { opacity: 0, x: -70 }, { opacity: 1, x: 0, duration: 0.8, ease: IN }, 4.42);
      tl.fromTo("#s1R", { opacity: 0, x: 70 }, { opacity: 1, x: 0, duration: 0.8, ease: IN }, 4.52);
      rise("#s1lt", 4.90);
      rise("#s1rt", 5.44);
      tl.fromTo("#s1star", { opacity: 0, scale: 0.4, rotation: -40 }, { opacity: 1, scale: 1, rotation: 0, duration: 0.8, ease: IN, transformOrigin: "50% 50%" }, 5.62);

      // s2 — trois réels, celui du milieu explose, puis niche → hook
      rise(".s2r", 7.0, { stagger: 0.09 });
      tl.to("#s2mid", { y: -26, scale: 1.06, duration: 0.7, ease: IN }, 7.72);
      tl.fromTo("#s2burst", { opacity: 0, scale: 0.5, rotation: -20 }, { opacity: 1, scale: 1, rotation: 0, duration: 0.9, ease: IN, transformOrigin: "50% 50%" }, 7.72);
      rise("#s2niche", 8.40);
      out("#s2niche", 9.10, { duration: 0.24 });
      rise("#s2hook", 9.36);

      // s3 — un script qui s'écrit, trois accroches au-dessus
      rise("#s3doc", 11.08);
      tl.fromTo(".s3l", { scaleX: 0 }, { scaleX: 1, duration: 0.5, ease: "expo.out", stagger: 0.14, immediateRender: false }, 11.25);
      rise(".s3c", 12.34, { stagger: 0.26 });

      // s4 — phrase IA barrée, puis coche
      rise("#s4q", 13.85);
      draw("#s4hl", 14.66, 0.45);
      out("#s4q", 15.0);
      tl.fromTo("#s4ok", { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: D, ease: IN }, 15.14);

      // s5 — rush → skill → MP4
      rise("#s5a", 16.10);
      draw("#s5l1", 16.46, 0.5);
      pop("#s5b", 16.46);
      draw("#s5l2", 16.9, 0.5);
      rise("#s5c", 18.82);
      rise(".s5t", 16.6, { stagger: 0.1 });
      [17.16, 17.56, 18.02].forEach(t => tl.fromTo("#s5b", { scale: 1.07 }, { scale: 1, duration: 0.4, ease: IN, immediateRender: false }, t));
      tl.fromTo("#s5ok", { opacity: 0, scale: 0.5 }, { opacity: 1, scale: 1, duration: 0.6, ease: IN }, 19.34);

      // s6 — mon préféré : une vidéo longue devient trois shorts
      rise("#s6fav", 21.16);
      pop("#s6long", 21.80);
      out("#s6long", 23.30, { scale: 0.96 });
      rise(".s6s", 23.60, { stagger: 0.1 });

      // s7 — dossier de fichiers texte, 0 €
      rise(["#s7back", "#s7tab"], 24.42);
      rise("#s7front", 24.50);
      tl.fromTo(".s7d", { opacity: 0, y: 160 }, { opacity: 1, y: 0, duration: 0.8, ease: IN, stagger: 0.08 }, 24.98);
      rise("#s7path", 25.2);
      out("#s7path", 26.0, { duration: 0.24 });
      pop("#s7zero", 26.30);

      // s8 — commente SKILLS, abonne-toi, coche + DM
      rise("#s8bar", 27.50);
      const typed = document.getElementById("s8typed"), word = "SKILLS", ty = { n: 0 };
      tl.fromTo(ty, { n: 0 }, { n: word.length, duration: 0.5, ease: "none", onUpdate: () => { typed.textContent = word.slice(0, Math.round(ty.n)); } }, 27.62);
      tl.fromTo("#s8send", { scale: 1 }, { scale: 0.9, duration: 0.08, yoyo: true, repeat: 1, ease: "power2.out" }, 28.0);
      rise("#s8sub", 28.14);
      out(["#s8bar", "#s8sub"], 28.4);
      tl.fromTo("#s8ok", { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: D, ease: IN }, 28.61);
      tl.fromTo("#s8cur", { opacity: 0, x: 120, y: 90 }, { opacity: 1, x: 0, y: 0, duration: 0.7, ease: IN }, 28.7);
      rise("#s8dm", 29.07);
