from pyrevit import forms

def main():
    # CommandSwitchWindow example
    # ops = ['option1', 'option2', 'option3', 'option4']
    # switches = ['switch1', 'switch2']
    # cfgs = {'option1': {'background': '0xFF55FF'}}
    # selected_option, switch_states = forms.CommandSwitchWindow.show(
    #     ops,
    #     switches=switches,
    #     message='Select Option',
    #     config=cfgs
    # )
    # print("Selected Option:", selected_option)
    # print("Switch States:", switch_states)

    # ProgressBar example
    # with forms.ProgressBar(title='Processing...', step=10) as pb:
    #     for i in range(100):
    #         pb.update_progress(i + 1, 100)
    #         if pb.cancelled:
    #             print("Operation cancelled.")
    #             break

    # SelectFromList example
    # items = ['item1', 'item2', 'item3']
    # selected_items = forms.SelectFromList.show(items, button_name='Select Items', multiselect=True)
    # print("Selected Items:", selected_items)

if __name__ == "__main__":
    main()