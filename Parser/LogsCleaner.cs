using System.Text.RegularExpressions;

namespace Services;

public static class LogsCleaner
{
	static readonly Regex ErrorRegex = new Regex(
		@"(
			\berror[:\s]                |   # C/C++/GCC, Python, etc.
			\bfatal\s+error             |   # C/C++
			\bundefined\s+reference     |   # Linking errors
			\bsegmentation\s+fault      |   # Runtime
			\bexception\b               |   # Python/Java/etc.
			\btraceback\b               |   # Python
			\bfailed\b                  |   # General failure
			\bnot\s+found\b             |   # Missing dependency
			\bmissing\b                 |   # Missing file or command
			\bcannot\s+find\b           |   # Common in gcc/linker
			\bcannot\s+open\b           |   # File errors
			\bNo\s+such\s+file          |   # Missing includes/files
			\bcommand\s+not\s+found     |   # Shell errors
			\bundefined\s+symbol        |   # Linker
			\bE:\s                      |   # Debian/apt style
			\bFATAL:                    |   # Systemd/logs
			\bFAIL\b                    |   # Build scripts/tests
			\bfail:                     |   # Build logs
			\bError\s+\d{3}             # e.g., HTTP/compilation codes
		)",
		RegexOptions.IgnoreCase | RegexOptions.IgnorePatternWhitespace | RegexOptions.Compiled
	);

    public static string ExtractErrors(string logText)
    {
        var match = ErrorRegex.Match(logText);
        if (match.Success)
        {
            // Обрезаем строку от позиции первого совпадения до конца
            return logText.Substring(match.Index);
        }

        return string.Empty; // если нет ошибок
    }
}
