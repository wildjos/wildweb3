// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Inbox {
    string public message;
    int public counter;

    constructor(string memory initialMessage) {
        message = initialMessage;
        counter = 0;
    }

    function setMessage(string memory newMessage) public {
        require(keccak256(abi.encodePacked(newMessage)) != keccak256(abi.encodePacked(message)), "New message must be different");
        message = newMessage;
        counter += 1;
    }

    function doMath(int a, int b) public pure returns (int sum, int diff, int product, bool isZero) {
        sum = a + b;
        diff = b - a;
        product = a * b;
        isZero = (a == 0);
    }
}
