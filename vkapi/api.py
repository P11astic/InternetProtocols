import requests
import re


def make_req(id, token, method):
    return requests.get('https://api.vk.com/method/' + method + '.get?user_id=' + id + '&' + 'access_token=' + token + '&v=5.131').text

def get_usr_int_id(id):
    link = ''
    if 'https://vk.com/' in re.findall(r'https://vk.com/', id):
        link = id
    else:
        link = 'https://vk.com/' + id
    try:
        return requests.get(link).text.split('money&target=mail')[1].split('&')[0]
    except IndexError:
        print('Profile is hidden or non-existing')

def get_usr_name(id, token):
    name_sname = make_req(id, token, 'users').split('"')
    return(name_sname[7] + " " + name_sname[11])

def get_usr_group_count(id, token):
    a = make_req(id, token, 'groups').split('[')[0]
    ans = re.search(r'\d+', a).group(0)
    return ans

def get_usr_status(id, token):
    a = make_req(id, token, 'status').split("[")
    return(a[0][21:-3])

def get_usr_friends(id ,token):
    a = make_req(id, token, 'friends').split('[')[0]
    ans = re.search(r'\d+', a).group(0)
    return ans

def main():
    token = 'Place your token here'
    page = str(input('Please enter the link on user\'s page or user\'s VK id: '))
    id = get_usr_int_id(page)
    print('User\'s name: ' + get_usr_name(token=token, id=id))
    print('User\' status: ' + get_usr_status(token=token, id=id))
    print('User\' group count: ' + get_usr_group_count(token=token, id=id))
    print('User\' friends count: ' + get_usr_friends(token=token, id=id))

if __name__=='__main__':
    main()