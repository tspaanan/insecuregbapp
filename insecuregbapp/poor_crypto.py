def poor_substitution_cipher(raw_password, direction):
    alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    subst_alphabet = ['c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','a','b']
    subst_password = ''
    if direction == 'L':
        for c in raw_password:
            if c in subst_alphabet:
               subst_password += alphabet[subst_alphabet.index(c)]
            else:
                subst_password += c
        return subst_password
    else:
        for c in raw_password:
            if c in alphabet:
                subst_password += subst_alphabet[alphabet.index(c)]
            else:
                subst_password += c
        return subst_password

