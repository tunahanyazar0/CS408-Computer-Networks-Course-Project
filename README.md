# Cloud File Storage and Management System

This project implements a **Cloud File Storage and Management System** as part of a learning exercise in computer networks. It is a client-server application that uses TCP sockets for communication. The system enables file uploads, downloads, and management via a graphical user interface (GUI).

## Features

### Server
- Accepts multiple client connections simultaneously using threading.
- Stores uploaded files in a designated directory with metadata management.
- Ensures unique filenames for each client by appending client-specific identifiers.
- Supports the following operations:
  - File upload (with overwrite support).
  - File download.
  - File deletion (by the original uploader).
  - File list retrieval.
- Logs all server-side activities, errors, and notifications in the server GUI.
- Manages large files efficiently and ensures metadata consistency, even during abrupt shutdowns.

### Client
- Connects to the server with a unique username.
- Uploads and downloads files to/from the server.
- Requests and displays the list of available files along with their owners.
- Deletes files uploaded by the client.
- Notifies the uploader whenever their file is downloaded (if the uploader is online).
- Provides a user-friendly GUI for all operations and logs client-side activities.

## Project Structure

- **Server.py**  
  Implements the server application, including file storage, client connection handling, and a GUI for monitoring server-side activities.

- **Client.py**  
  Implements the client application, including file upload, download, deletion, and interaction features via a user-friendly GUI.

## Setup and Usage

### Prerequisites
- Python 3.x
- `Tkinter` (pre-installed with Python)
- Basic networking setup (server and client must be on the same network or accessible via public IP)

## Key Features

- **Concurrency**  
  The server uses threading to handle multiple client connections simultaneously.

- **GUI**  
  Both client and server applications feature intuitive GUIs built using `Tkinter`.

- **Data Integrity**  
  The server ensures unique filenames and manages large file uploads/downloads reliably.

- **Notifications**  
  The uploader is notified whenever another client downloads their file.

## Limitations
- Only ASCII-compatible files are supported.
- Server and clients must be on the same network or accessible via public IP.
