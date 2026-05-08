require('dotenv').config();
const { ethers } = require('ethers');

const provider = new ethers.JsonRpcProvider(process.env.API_URL);
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);

async function main() {
  console.log("Wysyłam transakcję...");
  
  const tx = await wallet.sendTransaction({
    to: "0x96e13c46FdCa784d389Bf487317F298b5a866622",
    value: ethers.parseEther("0.001"),
  });

  console.log("TX hash:", tx.hash);
  console.log("Czekam na potwierdzenie...");
  await tx.wait();
  console.log("Potwierdzona!");
  console.log("Etherscan:", `https://sepolia.etherscan.io/tx/${tx.hash}`);
}

main().catch(console.error);