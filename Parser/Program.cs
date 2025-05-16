using HtmlAgilityPack;
using System;
using System.Net.Http;
using System.Text.RegularExpressions;

class Program
{
	static async Task Main()
	{
		string logUrl = "https://rdb.altlinux.org/api/export/beehive/ftbfs?branch=sisyphus";

		HttpClient client = new HttpClient();
		string logContent = await client.GetStringAsync(logUrl);
		//logContent = "https://asdas asd httd a https://dsadad";
		var urls = Regex.Matches(logContent, @"https?://[^\s""'>]+")
				.Select(m => m.Value)
				.ToList();

		// foreach (string url in urls)
		// {
		// 	Console.WriteLine(url);
		// }
	}
}
