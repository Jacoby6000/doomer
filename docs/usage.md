> Complete a prompt
> `>complete $num_tokens_to_generate $text_to_complete`
>  
> Complete a prompt without repeating the prompt
> `>complete_no_repeat $num_tokens_to_generate $text_to_complete`
>  
> Simulate chat from a given channel
> `>simulate $channel_partial_name $num_messages_to_read $num_tokens_to_generate`
> 
> Simulate chat from a given channel from around a given time
> `>simulate_from $channel_partial_name $num_messages_to_read $num_tokens_to_generate $iso_date`
> 
> Answer a question, impersonating a user from a given channel.
> `>answer_as $channel_partial_name $user_partial_name $num_tokens_to_generate $question`
> 
> Set presence_penalty. Tune how often new topics will come up. 0 = avoid new topics, 100 = more new topics.
> `>presence_penalty $n`
> 
> Set frequency_penalty. Tune how often the ai repeats itself. 0 = more repetition, 100 = less repetition.
> `>frequency_penalty $n`
> 
> Set temperature. Tune how risky (random) the model is.  0 = not random, 100 = more random.
> `>temperature $n`
> 
> Adjust number of messages to ingest for an auto reply
> `>auto_reply_messages $n`
> 
> Globally adjust percent chance to auto reply (0 to 100)
> `>auto_reply_rate $n`
> 
> Adjust percent chance to auto reply in a given channel (0 to 100) overrides the global setting.
> `>auto_reply_rate_in $channel_partial_name $n`
> 
> Globally adjust percent chance to auto react (0 to 100)
> `>auto_react_rate $n`
> 
> Adjust percent chance to auto react in a given channel (0 to 100) overrides the global setting.
> `>auto_react_rate_in $channel_partial_name $n`
> 
> Send last `n` messages to hastebin.
> `>hastebin $n`
