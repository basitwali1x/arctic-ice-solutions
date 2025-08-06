// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title ArcticOptimizerNFT
 * @dev NFT contract for Arctic Ice Solutions performance optimization achievements
 */
contract ArcticOptimizerNFT is ERC721, ERC721URIStorage, Ownable {
    using Counters for Counters.Counter;
    
    Counters.Counter private _tokenIdCounter;
    
    struct Achievement {
        string title;
        string impact;
        string category;
        uint256 timestamp;
        uint256 performanceGain;
        address contributor;
    }
    
    mapping(uint256 => Achievement) public achievements;
    mapping(address => uint256[]) public contributorTokens;
    mapping(string => bool) public categoryExists;
    
    event AchievementMinted(
        uint256 indexed tokenId,
        address indexed contributor,
        string title,
        string category,
        uint256 performanceGain
    );
    
    constructor() ERC721("Arctic Optimizer", "ARCTIC") {}
    
    /**
     * @dev Mint NFT for performance optimization achievement
     * @param _to Address to mint NFT to
     * @param _title Achievement title
     * @param _impact Description of impact
     * @param _category Achievement category (e.g., "Bundle Optimization", "Error Reduction")
     * @param _performanceGain Percentage performance improvement
     * @param _tokenURI Metadata URI for the NFT
     */
    function mintAchievement(
        address _to,
        string memory _title,
        string memory _impact,
        string memory _category,
        uint256 _performanceGain,
        string memory _tokenURI
    ) external onlyOwner {
        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();
        
        achievements[tokenId] = Achievement({
            title: _title,
            impact: _impact,
            category: _category,
            timestamp: block.timestamp,
            performanceGain: _performanceGain,
            contributor: _to
        });
        
        contributorTokens[_to].push(tokenId);
        categoryExists[_category] = true;
        
        _safeMint(_to, tokenId);
        _setTokenURI(tokenId, _tokenURI);
        
        emit AchievementMinted(tokenId, _to, _title, _category, _performanceGain);
    }
    
    /**
     * @dev Batch mint NFTs for team achievements
     */
    function batchMintTeamAchievements(
        address[] memory _contributors,
        string[] memory _titles,
        string[] memory _impacts,
        string[] memory _categories,
        uint256[] memory _performanceGains,
        string[] memory _tokenURIs
    ) external onlyOwner {
        require(
            _contributors.length == _titles.length &&
            _titles.length == _impacts.length &&
            _impacts.length == _categories.length &&
            _categories.length == _performanceGains.length &&
            _performanceGains.length == _tokenURIs.length,
            "Array lengths must match"
        );
        
        for (uint256 i = 0; i < _contributors.length; i++) {
            mintAchievement(
                _contributors[i],
                _titles[i],
                _impacts[i],
                _categories[i],
                _performanceGains[i],
                _tokenURIs[i]
            );
        }
    }
    
    /**
     * @dev Get all tokens owned by a contributor
     */
    function getContributorTokens(address _contributor) 
        external 
        view 
        returns (uint256[] memory) 
    {
        return contributorTokens[_contributor];
    }
    
    /**
     * @dev Get achievement details by token ID
     */
    function getAchievement(uint256 _tokenId) 
        external 
        view 
        returns (Achievement memory) 
    {
        require(_exists(_tokenId), "Token does not exist");
        return achievements[_tokenId];
    }
    
    /**
     * @dev Get total performance gain by contributor
     */
    function getTotalPerformanceGain(address _contributor) 
        external 
        view 
        returns (uint256) 
    {
        uint256[] memory tokens = contributorTokens[_contributor];
        uint256 totalGain = 0;
        
        for (uint256 i = 0; i < tokens.length; i++) {
            totalGain += achievements[tokens[i]].performanceGain;
        }
        
        return totalGain;
    }
    
    /**
     * @dev Get leaderboard of top contributors
     */
    function getTopContributors(uint256 _limit) 
        external 
        view 
        returns (address[] memory, uint256[] memory) 
    {
        // Note: This is a simplified implementation
        // In production, you'd want to maintain a sorted list
        address[] memory topAddresses = new address[](_limit);
        uint256[] memory topGains = new uint256[](_limit);
        
        // Implementation would require additional data structures
        // for efficient sorting and retrieval
        
        return (topAddresses, topGains);
    }
    
    // Override required functions
    function _burn(uint256 tokenId) 
        internal 
        override(ERC721, ERC721URIStorage) 
    {
        super._burn(tokenId);
    }
    
    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }
    
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
