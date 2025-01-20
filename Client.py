import socket
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import simpledialog 
import os
import time



class FileClient:
    def __init__(self):
        # initializing the client socket, server address, username, download directory and lock
        self.client_socket = None
        self.server_address = None
        self.username = None
        self.download_directory = ''
        self.lock = threading.Lock()
    

    # setting up the GUI
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Client GUI")
        
        # ip address entry
        self.ip_label = tk.Label(self.root, text="Server IP:")
        self.ip_label.grid(row=0 ,column= 0,padx=5,pady = 5,sticky="nswe")
        self.ip_entry = tk.Entry(self.root)
        self.ip_entry.grid(row=0 ,column= 1,padx=5,pady = 5,sticky="we")
        
        # port number entry -> to enter the port number
        self.port_label =tk.Label(self.root, text="Port Number:")
        self.port_label.grid(row=1 ,column= 0,padx=5,pady = 5,sticky="nswe")
        self.port_entry = tk.Entry(self.root)
        self.port_entry.grid(row=1 ,column= 1,padx=5,pady = 5,sticky="we")
        
        # username entry -> to enter the username
        self.username_label = tk.Label(self.root, text="Username:")
        self.username_label.grid(row=2 ,column= 0,padx=5,pady = 5,sticky="nswe")
        self.username_entry = tk.Entry(self.root)
        self.username_entry.grid(row=2 ,column= 1,padx=5,pady = 5,sticky="we")
        
        # connect button -> to connect to the server
        self.connect_button = tk.Button(self.root, text="Connect", command=self.connect_to_server)
        self.connect_button.grid(row=0 ,column= 3,padx=5,pady = 5,sticky="we")
        self.select_folder_button = tk.Button(self.root, text="Select Download Folder", command=self.select_download_folder)
        self.select_folder_button.grid(row=1 ,column= 3,padx=5,pady = 5,sticky="we")
        
        # log box -> to display the logs
        self.log_box = tk.Listbox(self.root, width=80)
        self.log_box.grid(row=3 ,rowspan=3,column= 0,columnspan=8,padx=5,pady = 5,sticky="nswe")

        # file box -> to display the files in the server
        self.file_box = tk.Listbox(self.root,width= 80)
        self.file_box.grid(row=0 ,rowspan=3,column= 5,columnspan=3,padx=5,pady = 5,sticky="nswe")
        
        # buttons to upload, download, request file list and delete file
        tk.Button(self.root, text="Upload File", command=self.upload_file).grid(row=6 ,column= 0,padx=5,pady = 5,sticky="nswe")
        tk.Button(self.root, text="Download File", command=self.download_file).grid(row=6 ,column= 1,padx=5,pady = 5,sticky="nswe")
        tk.Button(self.root, text="Request File List", command=self.request_file_list).grid(row=6 ,column= 2,padx=5,pady = 5,sticky="nswe")
        tk.Button(self.root, text="Delete File", command=self.delete_file).grid(row=6 ,column= 3,padx=5,pady = 5,sticky="nswe")
        # button to disconnect from the server
        tk.Button(self.root, text="Disconnect", command=self.disconnect_button).grid(row=6 ,column= 4,padx=5,pady = 5,sticky="nswe")
        self.root.grid_columnconfigure(0,weight=3)
        self.root.grid_columnconfigure(1,weight=3)
        self.root.grid_columnconfigure(2,weight=1)
        self.root.grid_columnconfigure(3,weight=1)
        self.root.grid_columnconfigure(4,weight=1)
        self.root.grid_columnconfigure(5,weight=30)
        self.root.grid_columnconfigure(6,weight=30)
        self.root.grid_columnconfigure(7,weight=30)
        
        self.root.grid_rowconfigure(0,weight=10)
        self.root.grid_rowconfigure(1,weight=10)
        self.root.grid_rowconfigure(2,weight=10)
        self.root.grid_rowconfigure(3,weight=10)
        self.root.grid_rowconfigure(4,weight=10)
        self.root.grid_rowconfigure(5,weight=10)
        self.root.grid_rowconfigure(6,weight=1)

        # closing the window
        self.root.protocol("WM_DELETE_WINDOW", self.disconnect)
        # running the GUI
        self.root.mainloop()
    
    
    # connecting to the server
    def connect_to_server(self):
        # acquiring the lock
        self.lock.acquire()
        # getting the ip address, port number and username 
        ip = self.ip_entry.get()
        port = int(self.port_entry.get())
        self.username = self.username_entry.get().strip()
        # checking if the username is empty
        if not self.username:
            self.log("Error: Username cannot be empty")
            self.lock.release()
            return
        # checking if the ip address is empty
        if self.client_socket != None and is_socket_connected(self.client_socket):
            self.log("Already connected to a server. Please disconnect before connecting again")
            self.lock.release()
            return

        # after checking, connecting to the server
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((ip, port))
            self.client_socket.sendall(self.username.encode())
            self.log(f"Connecting to server at {ip}:{port} as {self.username}")
            
            # release the lock after connecting
            self.lock.release()
            # starting a new thread to listen to the server messages
            threading.Thread(target=self.listen_to_server).start()
            
        except Exception as e:
            self.log(f"Connection failed: {e}")
            self.lock.release()

    # listening to the server messages
    def listen_to_server(self):
        # running the loop to listen to the server messages
        while True: 
            time.sleep(0.4)
            self.lock.acquire()
            
            if is_socket_connected(self.client_socket):
             # setting the socket to non-blocking
             self.client_socket.setblocking(False)
             try:
                # receiving the message from the server
                message = self.client_socket.recv(1024).decode()
                if message: # if the message is not empty
                    if message == "ERROR: Username already in use": # if the username is already in use
                        self.client_socket.close() # closing the socket
                    
                    self.log(message) # logging the message 
                    self.lock.release() # releasing the lock
                    
             except BlockingIOError: # if the socket is in blocking mode
                self.lock.release() # releasing the lock
                pass 
             except:
                self.log("Connection to server is lost")  
                self.client_socket.close() # closing the socket
                self.lock.release() # releasing the lock
                break
            else:
                self.lock.release()
                break

    # selecting the download folder
    def select_download_folder(self): 
        self.download_directory = filedialog.askdirectory() # asking the user to select the download directory
        self.log(f"Selected download directory: {self.download_directory}") # logging the selected download directory

    # uploading the file
    def upload_file(self):
     if self.client_socket != None and is_socket_connected(self.client_socket):
         
         # if the client socket is not connected
         if not self.client_socket:
             self.log("Not connected to the server.")
             
             return
         
        # asking the user to select the file
         file_path = filedialog.askopenfilename()
         if not file_path:
             self.log("No file selected for upload.")
             
             return
         self.lock.acquire() # acquiring the lock
         self.client_socket.setblocking(True) # setting the socket to blocking mode
         
        # getting the filename
         filename = os.path.basename(file_path)
         self.client_socket.sendall(f"UPLOAD {filename}".encode())
         

         # Wait for server acknowledgment before sending file
         response = self.client_socket.recv(1024).decode()
         # if the response is not ready
         if response != "READY" and response != "READY2":
             self.log(f"Upload failed: {response}") # logging the message
             self.lock.release() # releasing the lock
             return
         

         # Open the file in binary mode and send it in chunks
         try:
             with open(file_path, 'rb') as file:
                 while True:
                     chunk = file.read(1024 * 1024)  # Read in 1 MB chunks
                     
                     if not chunk:
                         # If no more data, send EOF and break
                         self.client_socket.sendall(b"EOF")
                         break
                     
                     # Send the chunk
                     self.client_socket.sendall(chunk)
 
                 
                 if response == "READY":
                   self.log(f"Uploaded '{filename}' to the server")
                 else:
                    self.log(f"{filename} already exists in the server. Overwriting the file")
 
                 # Receive upload success confirmation
                 confirmation = self.client_socket.recv(1024).decode()
                 self.lock.release()
         except Exception as e:
             self.log(f"Upload failed: {str(e)}")
             self.lock.release()
     else:
          self.log("ERROR: You must be connected to a server to upload file")
         
          
    # downloading the file
    def download_file(self):
        if not self.download_directory:
            # if the download directory is not selected
            if self.client_socket != None and is_socket_connected(self.client_socket):
             self.log("ERROR: You must choose download directory before downloading a file")
             return
            else:
                self.log("ERROR: You must be connected to a server to download file")
                return

        # if the client socket is connected
        if self.client_socket != None and is_socket_connected(self.client_socket):
            # if the client socket is not connected
           if not self.client_socket:
               self.log("Not connected to the server.")
               
               return
            #   if the download directory is not selected
           if not self.download_directory:
               self.log("Please select a download directory first.")
               
               return

            # asking the user to enter the filename and the uploader
           filename = self.request_file_input("Enter the filename to download:")
           if not filename:
               self.log("Please enter a filename")
               
               return
           uploader = self.request_file_input("Enter uploader's name:")
           if not uploader:
               self.log("Please enter the owner of the file")
               
               return
            # getting the file path
           file_path = os.path.join(self.download_directory, filename)

           if not filename or not uploader:
               
               return
           # Acquire the lock and set the socket to blocking mode
           self.lock.acquire()
           self.client_socket.setblocking(True)

           try:
            # Send download request to the server
               self.client_socket.sendall(f"DOWNLOAD {uploader} {filename}".encode())

            # Wait for initial server response
               response = self.client_socket.recv(1024).decode()
               if response.startswith("ERROR"):
                   self.log(response)
                   self.lock.release()
                   return
               elif response != "READY":
                   raise Exception("Unexpected server response")


            # Create a buffer to store incoming data
               buffer = b""
            
               with open(file_path, 'wb') as file:
                   while True:
                       chunk = self.client_socket.recv(1024 * 1024)  # Receive 1MB at a time
                       if not chunk:
                           break
                    
                    # Add the chunk to our buffer
                       buffer += chunk
                    
                    # Check if EOF marker is in the buffer
                       if b"EOF" in buffer:
                        # Write everything other than EOF to the file
                           file_data = buffer.split(b"EOF")[0]
                           file.write(file_data)
                           break
                    
                    # Check if we have enough data to write
                    # Keep a small buffer in case EOF is split across chunks
                       if len(buffer) > 1024 * 1024:  # 1MB
                           file.write(buffer[:-3])  # Keep last 3 bytes in case they're part of EOF
                           buffer = buffer[-3:]

               self.log(f"Successfully downloaded '{filename}' from {uploader} to {self.download_directory}")
               self.lock.release()

           except Exception as e:
               self.lock.release()
               self.log(f"Download failed: {str(e)}")
               if os.path.exists(file_path):
                   os.remove(file_path)  # Clean up partial download if error occurs
        else:
            self.log("ERROR: You must be connected to a server to download file")


    def delete_file(self):
        # if the client socket is connected
        if self.client_socket != None and is_socket_connected(self.client_socket):
         # take the file name from the user
         filename = self.request_file_input("Enter the filename to delete:")
         if filename:
            self.client_socket.sendall(f"DELETE {filename}".encode())
            self.lock.acquire()
            self.client_socket.setblocking(True) # set the socket to blocking mode 
        # receive the message from the server
         try:
            message = self.client_socket.recv(1024).decode()
            self.log(message)
         except:
            self.log("File cannot be deleted")
         self.lock.release()
        else:
            self.log("ERROR: You must be connected to a server to delete file")
            

    def request_file_list(self):
        # if the client socket is connected
        if self.client_socket != None and is_socket_connected(self.client_socket):
         try:
            # acquire the lock and set the socket to blocking mode, send the message to the server
            self.lock.acquire()
            self.file_box.delete(0, tk.END)
            self.client_socket.setblocking(True)
            self.client_socket.sendall("LIST_FILES".encode())
            message = self.client_socket.recv(1024).decode() # receive the message from the server
            for x in message.split("[^]"): 
              self.log_to_files(x) # log the message
            self.lock.release()
            self.log("Successfully recieved the file list")
         except:
             self.log("ERROR: An error occured while requesting the file list")

        else:
            self.log("ERROR: You must be connected to a server to request file list")

    # requesting the file input
    def request_file_input(self, prompt):
        return simpledialog.askstring("Input", prompt)

    # logging the message
    def log(self, message):
        self.log_box.insert(tk.END, message)
        # this line of code is for the scrollbar to automatically scroll down to the last message
        self.log_box.yview(tk.END)

    # logging the message to the file
    def log_to_files(self,message):
        self.file_box.insert(tk.END, message)
        self.file_box.yview(tk.END)

    def disconnect(self):
     if self.client_socket:
        try:
            self.client_socket.sendall("DISCONNECT".encode())
            self.log("Disconnected from server")
            self.client_socket.close()
        except Exception as e:
            self.log(f"Error during disconnect: {e}")
        finally:
            self.client_socket = None  # Ensure the socket is set to None

     self.root.destroy()  # Close the Tkinter window
    def disconnect_button(self):
        self.file_box.delete(0, tk.END)
        if self.client_socket == None:
            self.log("Error: Cannot disconnect because no connection were made")
        elif self.client_socket.fileno() != -1:
            self.lock.acquire()
            self.client_socket.sendall("DISCONNECT".encode())
            self.log("Disconnected from server")
            self.client_socket.close()
            self.lock.release()
        else:
            self.log("Error: Cannot disconnect because no connection were made")
     
    
def is_socket_connected(client_socket):
      try:
        # Check if peer name exists; if it raises an error, not connected
        client_socket.getpeername()
        return True
      except socket.error:
        return False
    
        

if __name__ == "__main__":
    FileClient().setup_gui()




