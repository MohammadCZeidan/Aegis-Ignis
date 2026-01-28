export function Logo({ className = "h-10 w-10" }: { className?: string }) {
  return (
    <svg 
      viewBox="0 0 512 512" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Shield Background */}
      <path d="M256 32L96 96V240C96 368 256 480 256 480C256 480 416 368 416 240V96L256 32Z" fill="#2C3E50"/>
      <path d="M256 48L112 104V240C112 356 256 460 256 460C256 460 400 356 400 240V104L256 48Z" fill="#34495E"/>
      
      {/* Split Shield */}
      <path d="M256 48L112 104V240C112 356 256 460 256 460V48Z" fill="#2980B9"/>
      <path d="M256 48V460C256 460 400 356 400 240V104L256 48Z" fill="#1E3A5F"/>
       <circle cx="180" cy="180" r="8" fill="#3498DB" opacity="0.6"/>
      <circle cx="200" cy="200" r="6" fill="#3498DB" opacity="0.6"/>
      <circle cx="160" cy="220" r="6" fill="#3498DB" opacity="0.6"/>
      <line x1="180" y1="180" x2="200" y2="200" stroke="#3498DB" strokeWidth="2" opacity="0.6"/>
      <line x1="200" y1="200" x2="160" y2="220" stroke="#3498DB" strokeWidth="2" opacity="0.6"/>
      
      {/* Fire/Flame (Right) */}
      <path d="M300 200C300 200 320 180 320 160C320 140 310 130 300 140C300 140 290 120 280 130C270 140 280 160 280 180C280 200 290 210 300 220C310 210 300 200 300 200Z" fill="#E67E22"/>
      <path d="M305 190C305 190 315 175 315 165C315 155 310 150 305 155C305 155 300 145 295 150C290 155 295 165 295 175C295 185 300 190 305 195C310 190 305 190 305 190Z" fill="#F39C12"/>
      
      {/* Stars (Bottom) */}
      <circle cx="220" cy="350" r="12" fill="#F1C40F"/>
      <circle cx="256" cy="370" r="10" fill="#F1C40F"/>
      <circle cx="292" cy="350" r="12" fill="#F1C40F"/>
      
      {/* Top Flame */}
      <path d="M256 0C256 0 280 40 280 70C280 85 270 95 256 95C242 95 232 85 232 70C232 40 256 0 256 0Z" fill="#E74C3C"/>
      <path d="M256 15C256 15 270 45 270 65C270 75 264 82 256 82C248 82 242 75 242 65C242 45 256 15 256 15Z" fill="#F39C12"/>
      <path d="M256 25C256 25 265 50 265 62C265 68 261 72 256 72C251 72 247 68 247 62C247 50 256 25 256 25Z" fill="#FFF"/>
      
      {/* Shield Border */}
      <path d="M256 32L96 96V240C96 368 256 480 256 480C256 480 416 368 416 240V96L256 32Z" stroke="#34495E" strokeWidth="8" fill="none"/>
    </svg>
  );
}
