using System;
using System.Diagnostics;
namespace TF_IDF;

public static class Python
{
	public static string ExecutePythonScript(string scriptPath, string arguments = "")
	{
		try
		{
			ProcessStartInfo start = new ProcessStartInfo
			{
				FileName = "python3", // или полный путь к python.exe
				Arguments = $"\"{scriptPath}\" {arguments}",
				UseShellExecute = false,
				RedirectStandardOutput = true,
				RedirectStandardError = true,
				CreateNoWindow = true
			};

			using (Process process = Process.Start(start))
			{
				using (System.IO.StreamReader reader = process.StandardOutput)
				{
					string result = reader.ReadToEnd();
					string errors = process.StandardError.ReadToEnd();

					if (!string.IsNullOrEmpty(errors))
					{
						throw new Exception($"Ошибка Python: {errors}");
					}

					return result;
				}
			}
		}
		catch (Exception ex)
		{
			return $"Ошибка: {ex.Message}";
		}
	}
}
