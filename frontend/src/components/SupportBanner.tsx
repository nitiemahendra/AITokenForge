import { useState } from "react";
import { Heart, X } from "lucide-react";

interface Props {
  savingsPercent?: number;
}

export default function SupportBanner({ savingsPercent }: Props) {
  const [dismissed, setDismissed] = useState(
    () => localStorage.getItem("tf_support_dismissed") === "1"
  );

  if (dismissed) return null;

  const dismiss = () => {
    localStorage.setItem("tf_support_dismissed", "1");
    setDismissed(true);
  };

  return (
    <div className="flex items-center gap-3 px-4 py-2.5 bg-[#0d1117] border border-orange-500/20 rounded-lg text-sm">
      <Heart size={14} className="text-orange-400 flex-shrink-0" />
      <span className="text-slate-400 flex-1">
        {savingsPercent && savingsPercent > 0 ? (
          <>You saved <strong className="text-orange-400">{savingsPercent.toFixed(0)}%</strong> in tokens.{" "}</>
        ) : null}
        If TokenForge helps reduce your AI costs,{" "}
        <a
          href="https://github.com/sponsors/nitiemahendra"
          target="_blank"
          rel="noopener noreferrer"
          className="text-orange-400 hover:text-orange-300 underline underline-offset-2"
        >
          consider supporting the project ❤️
        </a>
        .
      </span>
      <button
        onClick={dismiss}
        className="text-slate-600 hover:text-slate-400 transition-colors flex-shrink-0"
        title="Dismiss"
      >
        <X size={14} />
      </button>
    </div>
  );
}
