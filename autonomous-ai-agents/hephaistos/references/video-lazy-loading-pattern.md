# Video Lazy Loading Pattern (PingPongVideo)

## Problema
Vídeos de fundo em hero + contato carregam simultaneamente no page load, consumindo bandwidth e causando jank.

## Padrão
```tsx
function PingPongVideo({ src, className, opacity = "opacity-30" }: { src: string; className?: string; opacity?: string }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const rafRef = useRef<number>(0);
  const reversingRef = useRef(false);
  const [isVisible, setIsVisible] = useState(false);

  // 1. IntersectionObserver — só observa, não carrega
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (prefersReduced.matches) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { rootMargin: "200px" } // 200px antes de entrar no viewport
    );
    observer.observe(video);
    return () => observer.disconnect();
  }, []);

  // 2. Ping-pong effect — só roda quando visível
  useEffect(() => {
    if (!isVisible) return;
    const video = videoRef.current;
    if (!video) return;
    // ... (play/ping-pong logic)
  }, [isVisible]);

  return (
    <video 
      ref={videoRef} 
      src={src} 
      muted 
      playsInline
      preload={isVisible ? "auto" : "none"} // 3. preload condicional
      className={`w-full h-full object-cover ${opacity} ${className || ""}`} 
    />
  );
}
```

## Ganhos
- Vídeo do contato (01.mp4) só carrega quando usuário rola até a seção
- Reduz ~50% da carga inicial em páginas com múltiplos vídeos
- `prefers-reduced-motion` respeitado

## Referência
- Validado no Desconsultor, 2026-06-16
