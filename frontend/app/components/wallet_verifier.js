// wallet_verifier.js
"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function WalletVerifier() {
  const [isOpen, setIsOpen] = useState(true);
  const [wallet, setWallet] = useState("");
  const [verification, setVerification] = useState(null);

    const handleVerify = () => {
    if (!wallet) {
        setVerification("Enter a wallet address");
    } else {
        // Placeholder logic with reason
        const isSybil = Math.random() > 0.5;
        if (isSybil) {
        setVerification(
            "⚠ Strong Sybil evidence.\nReason: Funding link found, 12 subgroups source back to 0x01c9…0bb0."
        );
        } else {
        setVerification("✅ No cluster found");
        }
    }
    };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          className="relative w-[15vw] h-[20vh] p-3 rounded-xl bg-gray-900/20 backdrop-blur-md border border-cyan-400 overflow-hidden"
        >
         

          {/* Collapse button (fancy circular) */}
          <button
            onClick={() => setIsOpen(false)}
            className="absolute top-2 right-2 w-6 h-6 flex items-center justify-center rounded-full border border-cyan-400 text-cyan-400 hover:bg-cyan-400 hover:text-gray-900 transition"
          >
            ×
          </button>

            <div className="flex flex-col gap-2">

            <h2 className="text-[18px] font-bold text-cyan-400 tracking-wide">
                Wallet Verifier
            </h2>

            {/* Input immediately below the title */}
            <input
                type="text"
                placeholder="0x123...abc"
                value={wallet}
                onChange={(e) => setWallet(e.target.value)}
                className="w-full p-1 rounded-md bg-gray-900/50 border border-cyan-400 text-white text-xs focus:outline-none focus:ring-1 focus:ring-cyan-300 placeholder:text-gray-400"
            />

            <button
                onClick={handleVerify}
                className="w-full py-1 rounded-md bg-gradient-to-r from-cyan-400 to-green-400 text-white text-xs font-semibold tracking-wide hover:brightness-110 transition"
            >
                Verify
            </button>

            {verification && (
                <p className="text-gray-300 text-[10px]">{verification}</p>
            )}

            </div>

          {/* Fancy gradient wave animation */}
          <style jsx>{`
            .border-gradient {
              border-image: linear-gradient(135deg, #00ffe0, #00bfff, #00ffe0, #00bfff);
              border-image-slice: 1;
            }
            .animate-border-wave {
              position: relative;
              overflow: hidden;
            }
            .animate-border-wave::after {
              content: '';
              position: absolute;
              top: -50%;
              left: -50%;
              width: 200%;
              height: 200%;
              background: linear-gradient(
                60deg,
                rgba(0,255,224,0.1) 0%,
                rgba(0,191,255,0.2) 50%,
                rgba(0,255,224,0.1) 100%
              );
              animation: wave 3s linear infinite;
              transform: rotate(45deg);
            }
            @keyframes wave {
              0% { transform: translate(-50%, -50%) rotate(45deg); }
              50% { transform: translate(50%, 50%) rotate(45deg); }
              100% { transform: translate(-50%, -50%) rotate(45deg); }
            }
          `}</style>
        </motion.div>
      )}

      {!isOpen && (
        <motion.button
          onClick={() => setIsOpen(true)}
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          className="bg-gradient-to-r from-cyan-400 to-green-400 text-white font-semibold py-2 px-2 rounded-full shadow-sm text-sm"
        >
          Verify Wallet
        </motion.button>
      )}
    </AnimatePresence>
  );
}