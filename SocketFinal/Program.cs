using System;
using System.Net;
using System.Net.Http;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace SocketFinal
{
    public abstract class Moneda
    {
        public abstract string Nombre { get; }
        public abstract string Simbolo { get; }
        public abstract Task<double> ObtenerPrecioEnPesos();
    }

    public class Dolar : Moneda
    {
        private const string ApiServiceUrl = "https://api.exchangerate-api.com/v4/latest/USD";
        public override string Nombre => "Dolar";
        public override string Simbolo => "USD";

        public override async Task<double> ObtenerPrecioEnPesos()
        {
            using (HttpClient httpClient = new HttpClient())
            {
                try
                {
                    string response = await httpClient.GetStringAsync(ApiServiceUrl);

                    int startIndex = response.IndexOf("\"MXN\":") + 6;
                    int endIndex = response.IndexOf(',', startIndex);
                    string precioEnPesosText = response.Substring(startIndex, endIndex - startIndex);
                    return double.Parse(precioEnPesosText);
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error al obtener datos de la divisa: {ex.Message}");
                    return -1;
                }
            }
        }
    }

    public class ServidorSocket
    {
        private TcpListener listener;
        private int contador;
        private object contadorLock;
        private Moneda moneda;

        public ServidorSocket(Moneda moneda)
        {
            listener = new TcpListener(IPAddress.Parse("127.0.0.1"), 8888);
            contador = 0;
            contadorLock = new object();
            this.moneda = moneda;
        }

        public void Iniciar()
        {
            try
            {
                listener.Start();
                Console.WriteLine($"Servidor escuchando en 127.0.0.1:8888 para {moneda.Nombre}");

                while (true)
                {
                    TcpClient client = listener.AcceptTcpClient();
                    Thread clientThread = new Thread(HandleClient);
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

        private void HandleClient(object obj)
        {
            TcpClient tcpClient = (TcpClient)obj;

            lock (contadorLock)
            {
                contador++;
            }

            NetworkStream clientStream = tcpClient.GetStream();
            var precioEnPesos = moneda.ObtenerPrecioEnPesos().Result;

            string message = $"Se ha consultado {contador} veces - Precio de {moneda.Nombre} en pesos: {precioEnPesos}";
            byte[] data = Encoding.ASCII.GetBytes(message);

            IPEndPoint clientEndPoint = (IPEndPoint)tcpClient.Client.RemoteEndPoint;
            string clientAddress = clientEndPoint.Address.ToString();
            int clientPort = clientEndPoint.Port;

            Console.WriteLine($"Cliente conectado desde {clientAddress}:{clientPort}: {message}");

            clientStream.Write(data, 0, data.Length);
            tcpClient.Close();
        }
    }

    class Program
    {
        static void Main()
        {
            Moneda dolar = new Dolar();
            ServidorSocket servidor = new ServidorSocket(dolar);
            servidor.Iniciar();
        }
    }
}
