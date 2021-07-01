> Complete a prompt
> `>complete $num_tokens_to_generate $text_to_complete`
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
> Get bot settings
> `>get_settings`
>  
> Get model settings
> `>get_model_settings $model_name`
>  
> Update bot settings
> `>update_settings $setting_name $value`
>  
> Update bot settings for a channel
> `>update_channel_settings $setting_name $channel_name $value`
>  
> Update model settings
> `>update_model_settings $setting_name $value $model_name`
>  
> Set default model
> `>set_default_model $model_name`
> 
> Send last `n` messages to hastebin.
> `>hastebin $n`
