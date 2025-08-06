const { ethers } = require("hardhat");
const fs = require("fs");

async function main() {
  console.log("🚀 Deploying Arctic Optimizer NFT contract...");
  
  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);
  console.log("Account balance:", (await deployer.getBalance()).toString());

  const ArcticOptimizerNFT = await ethers.getContractFactory("ArcticOptimizerNFT");
  const arcticNFT = await ArcticOptimizerNFT.deploy();
  
  await arcticNFT.deployed();
  console.log("✅ ArcticOptimizerNFT deployed to:", arcticNFT.address);

  console.log("\n🎖️ Minting achievement NFTs...");
  
  const achievements = [
    {
      address: "0x1234567890123456789012345678901234567890", // Replace with actual address
      title: "Performance Pioneer",
      impact: "Reduced LCP by 1.1s and achieved 99.97% error-free sessions",
      category: "Full Stack Optimization",
      performanceGain: 46,
      tokenURI: "ipfs://QmYourHashHere/performance-pioneer.json"
    },
    {
      address: "0x2345678901234567890123456789012345678901", // Replace with actual address
      title: "Bundle Optimizer",
      impact: "Reduced bundle size by 42% through advanced chunk splitting",
      category: "Bundle Optimization", 
      performanceGain: 42,
      tokenURI: "ipfs://QmYourHashHere/bundle-optimizer.json"
    },
    {
      address: "0x3456789012345678901234567890123456789012", // Replace with actual address
      title: "Error Boundary Guardian",
      impact: "Reduced error rate by 97% with comprehensive error handling",
      category: "Error Handling",
      performanceGain: 97,
      tokenURI: "ipfs://QmYourHashHere/error-guardian.json"
    },
    {
      address: "0x4567890123456789012345678901234567890123", // Replace with actual address
      title: "Cache Maestro",
      impact: "Improved cache hit rate from 35% to 89%",
      category: "Caching Strategy",
      performanceGain: 154,
      tokenURI: "ipfs://QmYourHashHere/cache-maestro.json"
    }
  ];

  for (let i = 0; i < achievements.length; i++) {
    const achievement = achievements[i];
    
    try {
      const tx = await arcticNFT.mintAchievement(
        achievement.address,
        achievement.title,
        achievement.impact,
        achievement.category,
        achievement.performanceGain,
        achievement.tokenURI
      );
      
      await tx.wait();
      console.log(`✅ Minted "${achievement.title}" NFT (Token ID: ${i})`);
    } catch (error) {
      console.error(`❌ Failed to mint "${achievement.title}":`, error.message);
    }
  }

  const deploymentInfo = {
    contractAddress: arcticNFT.address,
    deployerAddress: deployer.address,
    networkName: network.name,
    deploymentDate: new Date().toISOString(),
    achievements: achievements.map((achievement, index) => ({
      tokenId: index,
      ...achievement
    }))
  };

  fs.writeFileSync(
    "deployment-info.json",
    JSON.stringify(deploymentInfo, null, 2)
  );

  console.log("\n📄 Deployment information saved to deployment-info.json");
  
  if (network.name !== "hardhat" && network.name !== "localhost") {
    console.log("\n🔍 Verifying contract on Etherscan...");
    try {
      await hre.run("verify:verify", {
        address: arcticNFT.address,
        constructorArguments: [],
      });
      console.log("✅ Contract verified on Etherscan");
    } catch (error) {
      console.error("❌ Verification failed:", error.message);
    }
  }

  console.log("\n🎉 Deployment complete!");
  console.log(`Contract Address: ${arcticNFT.address}`);
  console.log(`View on Etherscan: https://etherscan.io/address/${arcticNFT.address}`);
  console.log(`OpenSea Collection: https://opensea.io/collection/arctic-optimizer`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
