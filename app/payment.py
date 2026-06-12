import uuid


class PaymentResult:
    def __init__(self, success, transaction_id, message):
        self.success = success
        self.transaction_id = transaction_id
        self.message = message


class StripeGateway:
    def process(self, amount, currency, details):
        card = details.get('card_number', '').replace(' ', '')
        if not card or len(card) < 13:
            return PaymentResult(False, None, 'Invalid card number.')
        return PaymentResult(
            True,
            f'stripe_{uuid.uuid4().hex[:16]}',
            f'Charge of ${amount:.2f} approved via Stripe (card ending {card[-4:]}).'
        )


class PayPalGateway:
    def process(self, amount, currency, details):
        email = details.get('paypal_email', '')
        if '@' not in email:
            return PaymentResult(False, None, 'Invalid PayPal email.')
        return PaymentResult(
            True,
            f'paypal_{uuid.uuid4().hex[:16]}',
            f'Payment of ${amount:.2f} approved via PayPal ({email}).'
        )


class MobileMoneyGateway:
    PROVIDERS = ['mtn', 'airteltigo']

    def process(self, amount, currency, details):
        provider = details.get('mobile_provider', '').lower()
        phone = details.get('mobile_phone', '').replace(' ', '').replace('-', '')
        if provider not in self.PROVIDERS:
            return PaymentResult(False, None, 'Unsupported mobile money provider.')
        if not phone or len(phone) < 10:
            return PaymentResult(False, None, 'Invalid mobile phone number.')
        return PaymentResult(
            True,
            f'momo_{uuid.uuid4().hex[:16]}',
            f'{provider.upper()} payment of ${amount:.2f} confirmed ({phone}).'
        )


GATEWAYS = {
    'stripe': StripeGateway(),
    'paypal': PayPalGateway(),
    'mobile_money': MobileMoneyGateway(),
}


def process_payment(method, amount, details, currency='USD'):
    gateway = GATEWAYS.get(method)
    if not gateway:
        return PaymentResult(False, None, f'Unsupported payment method: {method}')
    return gateway.process(amount, currency, details)
