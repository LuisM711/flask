using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

namespace SocketFinal
{
    public class Program
    {
        public static int contador = 0;

        static void Main()
        {
            IPAddress ipAddress = IPAddress.Parse("127.0.0.1");
            int port = 8888;
            TcpListener listener = new TcpListener(ipAddress, port);

            try
            {
                listener.Start();
                Console.WriteLine($"Servidor escuchando en {ipAddress}:{port}");

                while (true)
                {
                    TcpClient client = listener.AcceptTcpClient();
                    Thread clientThread = new Thread(new ParameterizedThreadStart(HandleClient));
                    clientThread.Start(client);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
            }
            finally
            {
                listener.Stop();
            }
        }

        static void HandleClient(object obj)
        {
            contador++;
            TcpClient tcpClient = (TcpClient)obj;
            NetworkStream clientStream = tcpClient.GetStream();
            string message = "Hola Mundo " + contador;
            byte[] data = Encoding.ASCII.GetBytes(message);
            IPEndPoint clientEndPoint = (IPEndPoint)tcpClient.Client.RemoteEndPoint;
            string clientAddress = clientEndPoint.Address.ToString();
            int clientPort = clientEndPoint.Port;
            Console.WriteLine($"Cliente conectado desde {clientAddress}:{clientPort}: {message}");
            clientStream.Write(data, 0, data.Length);
            tcpClient.Close();
        }
    }
}
