# Secured Socket Programming

## Overview

The Secured Socket Programming project aims to create a secure and private messaging system that allows users to send text messages and files while ensuring end-to-end encryption. This project provides secure communication, robust user authentication, and a user-friendly interface.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [System Architecture](#system-architecture)
- [Algorithms](#algorithms)
- [Analysis](#analysis)
- [Installation](#installation)
- [Usage](#usage)
- [Contributors](#contributors)
- [License](#license)

## Features

- **End-to-End Encryption**: Ensures that only the intended recipient can decrypt the messages and files.
- **User Authentication**: Users must authenticate themselves with a valid phone number and password.
- **File Transfer**: Users can securely send and receive files.
- **Message Retrieval**: Clients can request and securely receive their communication history.
- **User-Friendly Interface**: Intuitive interface for easy navigation and usage.
- **Secure Key Exchange**: Utilizes Diffie-Hellman key exchange for secure communication.

## Technologies Used

- **Programming Language**: Python
- **Cryptography Libraries**: PyCryptodome
- **Database**: MongoDB
- **Protocols**: Diffie-Hellman key exchange
- **Encryption Methods**: XOR encryption

## System Architecture

### Server-Side Architecture

- **User Authentication**: Authenticates users by checking credentials against a MongoDB database.
- **Key Generation**: Generates large prime numbers for secure communication.
- **Database Management**: Stores user data, messages, and files in MongoDB.
- **Message and File Handling**: Manages receipt, storage, and retrieval of text messages and files.

### Client-Side Architecture

- **User Authentication**: Sends phone number and password to the server for verification.
- **Key Exchange**: Generates encryption keys using server-provided prime numbers.
- **Message and File Transfer**: Securely sends and receives text messages and files.
- **User Interface**: Provides an intuitive interface for user interactions.

## Algorithms

### Generating Large Prime Numbers

- Utilizes the `number.getPrime()` function from PyCryptodome to generate large prime numbers.

### XOR Encryption

- Uses XOR operations with a symmetric key for securing text and file transmissions.

### Diffie-Hellman Key Exchange

- Establishes a shared secret key over an insecure communication channel using large prime numbers and modular arithmetic.

## Analysis

- **Exponential Complexity Across Tables**: Observes exponential growth in computational time with increasing bit length or number of iterations.
- **Trade-off Between Security and Efficiency**: Balances stronger security with larger bit lengths against computational efficiency.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/ityashag/SOCKET_PROGRAMMING.git
    ```
2. Navigate to the project directory:
    ```bash
    cd SOCKET_PROGRAMMING
    ```
## Usage

1. Start the server:
    ```bash
    python server.py
    ```
2. Start the client:
    ```bash
    python client.py
    ```

## Contributors

- **Vipul Verma**
  - GitHub: [vvsvipul](https://github.com/vvsvipul)
- **Yash Agarwal**
  - GitHub: [ityashag](https://github.com/ityashag)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
