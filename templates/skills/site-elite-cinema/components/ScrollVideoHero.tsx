"use client";

import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useEffect, useRef, useState } from "react";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger, useGSAP);
}

export interface ScrollVideoHeroProps {
  src: string;
  srcMobile?: string;
  posterSrc: string;
  durationVh?: number;
  pin?: boolean;
  scrub?: number;
  ariaLabel?: string;
  className?: string;
}

export default function ScrollVideoHero({
  src,
  srcMobile,
  posterSrc,
  durationVh = 200,
  pin = true,
  scrub = 0.3,
  ariaLabel = "Scroll-driven hero video",
  className,
}: ScrollVideoHeroProps): JSX.Element {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [shouldPreload, setShouldPreload] = useState(false);
  const [metadataReady, setMetadataReady] = useState(false);

  useEffect(() => {
    const node = containerRef.current;
    if (!node) return;
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setShouldPreload(true);
            observer.disconnect();
            break;
          }
        }
      },
      { rootMargin: "200% 0px" },
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    if (video.readyState >= 1) {
      setMetadataReady(true);
      return;
    }
    const onMeta = () => setMetadataReady(true);
    video.addEventListener("loadedmetadata", onMeta);
    return () => video.removeEventListener("loadedmetadata", onMeta);
  }, [shouldPreload]);

  useGSAP(
    () => {
      const video = videoRef.current;
      const container = containerRef.current;
      if (!video || !container || !metadataReady) return;

      const duration = Number.isFinite(video.duration) ? video.duration : 0;
      if (duration <= 0) return;

      video.pause();
      video.currentTime = 0;

      const tween = gsap.to(video, {
        currentTime: duration,
        ease: "none",
        scrollTrigger: {
          trigger: container,
          start: "top top",
          end: `+=${durationVh}%`,
          scrub,
          pin,
          anticipatePin: 1,
          invalidateOnRefresh: true,
        },
      });

      return () => {
        tween.scrollTrigger?.kill();
        tween.kill();
      };
    },
    { scope: containerRef, dependencies: [metadataReady, durationVh, pin, scrub] },
  );

  useEffect(() => {
    return () => {
      ScrollTrigger.getAll().forEach((t) => {
        if (t.trigger === containerRef.current) t.kill();
      });
    };
  }, []);

  const preloadAttr: "auto" | "metadata" | "none" = shouldPreload ? "auto" : "metadata";

  return (
    <div
      ref={containerRef}
      role="img"
      aria-label={ariaLabel}
      className={className}
      style={{ position: "relative", width: "100%", height: "100vh", overflow: "hidden", backgroundColor: "#0a0a0a" }}
    >
      <video
        ref={videoRef}
        muted
        playsInline
        preload={preloadAttr}
        poster={posterSrc}
        crossOrigin="anonymous"
        disableRemotePlayback
        style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }}
      >
        {srcMobile ? <source src={srcMobile} media="(max-width: 768px)" type="video/mp4" /> : null}
        <source src={src} type="video/mp4" />
      </video>
    </div>
  );
}
