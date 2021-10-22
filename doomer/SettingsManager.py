
class SettingsManager():

    def __init__(self, initial_settings, settings_rules): 
        self.rules = settings_rules
        self.settings = {}
        self.update_settings(initial_settings)

    def get_settings_help(rule_tree=self.rules, indent=0):
        help_text = ""
        for k in rule_tree:
            if k.startswith("__"):
                continue

            help_text = help_text + ("\t" * indent) + k + ": "
            if "__help" in rule_tree[k]:
                help_text = help_text + ("\t"*(indent + 1)) + rule_tree[k]["__help"] + "\n"
            if "__valid_values" in rule_tree[k]:
                help_text = help_text + ("\t"*(indent + 1)) + "valid values: " + str(rule_tree[k]["__valid_values"]) + "\n"
            help_text = help_text + "\n"
            help_text = help_text + get_settings_help(rule_tree[k], indent + 1)

        return help_text


    def get_setting(*path):
        cur_setting = self.settings
        for path_part in path:
            cur_setting = cur_setting[path_part]

        return cur_setting

    def get_settings():
        return this.settings

    def update_settings(settings, tree=self.settings, *path):
        for k in settings:
            if type(settings[k]) is dict:
                if k not in tree:
                    tree[k] = {}
                update_settings(settings[k], tree[k], path, k)
            else: 
                update_setting(settings[k], path)

    def update_setting(setting, *path):
        cur_rule = self.rules
        for path_part in path[:-1]:
            if path_part in cur_rule or "$var" in cur_rule:
                cur_rule = cur_rule[path]
            else:
                raise Exception("Invalid rule path " + ".".join(path) + " at " + path_part)

        converted_setting = setting
        if "__conversion" in cur_rule:
            converted_setting = cur_rule["__conversion"](setting)

        if "__valid_values" in cur_rule:
            if converted_setting in cur_rule["__valid_values"]:
                cur_rule[path[-1]] = converted_setting
            else:
                raise Exception("Invalid setting value " + str(converted_setting) + " at location " + ".".join(path) +"\n" + 
                                "Expected one of: " + ", ".join(cur_rule["__valid_values"]))
        elif "__validator" in cur_rule:
            if cur_rule["__validator"](converted_setting):
                cur_rule[path[-1]] = converted_setting
            else:
                raise Exception("Invalid setting value " + str(converted_setting) + " at location " + ".".join(path))
        else:
            cur_rule[path[-1]] = converted_setting

