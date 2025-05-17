def delBrain(answer):
	index = answer.find('</think>')
	newAnswer = answer[index + 8:]
	newAnswer = newAnswer.replace("+", "_").strip()
	return newAnswer
