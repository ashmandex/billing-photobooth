interface ChooseProps {
  onBack: () => void;
  onQrisPayment: () => void;
  onCashPayment: () => void;
}

export default function Choose({ onBack, onQrisPayment, onCashPayment }: ChooseProps) {
  return (
    <div id="content-2" className="flex flex-col items-center justify-center gap-[20px]">
      <span className="main-font text-[45px] text-[#2E4E3F] font-semibold leading-tight text-center">Pilih Metode Pembayaran</span>
      
      <div className="payment-options flex flex-col gap-[20px] w-full max-w-[500px]">
        <button 
          onClick={onQrisPayment}
          className="payment-option normal-font cursor-pointer hover:scale-98 hover:shadow-[0px_0px_0px_0px_#2E4E3F] transition-all duration-300 flex flex-row justify-center items-center gap-[15px] py-[18px] px-[25px] bg-[#5AA47C] rounded-[10px] text-[white] text-[22px] font-bold leading-tight border-3 border-[#2E4E3F] shadow-[2px_2px_0px_0px_#2E4E3F]"
        >
          Bayar dengan QRIS
        </button>
        
        <button 
          onClick={onCashPayment}
          className="payment-option normal-font cursor-pointer hover:scale-98 hover:shadow-[0px_0px_0px_0px_#2E4E3F] transition-all duration-300 flex flex-row justify-center items-center gap-[15px] py-[18px] px-[25px] bg-[#FF8C42] rounded-[10px] text-[white] text-[22px] font-bold leading-tight border-3 border-[#2E4E3F] shadow-[2px_2px_0px_0px_#2E4E3F]"
        >
          Bayar dengan Tunai / Voucher
        </button>
      </div>
      
      <button 
        onClick={onBack}
        className="back-button normal-font cursor-pointer hover:scale-98 hover:shadow-[0px_0px_0px_0px_#2E4E3F] transition-all duration-300 flex flex-row justify-center items-center gap-[10px] py-[12px] px-[20px] bg-[#CCCCCC] rounded-[10px] text-[#2E4E3F] text-[18px] font-bold leading-tight border-3 border-[#2E4E3F] shadow-[2px_2px_0px_0px_#2E4E3F]"
      >
        Kembali
      </button>
    </div>
  );
}
