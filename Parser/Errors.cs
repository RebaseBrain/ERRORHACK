namespace Entities;

class Error
{
	public string? namepackage
	{
		get; set;
	}
	public string? errortype
	{
		get; set;
	}
	public string? pathToLogFile
	{
		get; set;
	}
	private string? _fullLog
	{
		get; set;
	}
}
