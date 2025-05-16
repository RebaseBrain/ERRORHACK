using System;
using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace Entities;


public class FtbfsResponse
{
	[JsonPropertyName("request_args")]
	public Dictionary<string, object>? RequestArgs { get; set; }

	[JsonPropertyName("length")]
	public int? Length { get; set; }

	[JsonPropertyName("ftbfs")]
	public List<FtbfsPackage>? Ftbfs { get; set; }
}

public class FtbfsPackage
{
	[JsonPropertyName("branch")]
	public string? Branch { get; set; }

	[JsonPropertyName("hash")]
	public string? Hash { get; set; }

	[JsonPropertyName("name")]
	public string? Name { get; set; }

	[JsonPropertyName("epoch")]
	public int? Epoch { get; set; }

	[JsonPropertyName("version")]
	public string? Version { get; set; }

	[JsonPropertyName("release")]
	public string? Release { get; set; }

	[JsonPropertyName("arch")]
	public string? Arch { get; set; }

	[JsonPropertyName("updated")]
	public string? Updated { get; set; }

	[JsonPropertyName("ftbfs_since")]
	public string? FtbfsSince { get; set; }

	[JsonPropertyName("url")]
	public string? Url { get; set; }
}

