<?php

declare(strict_types = 1);

namespace App\Mail;

use Brevo\Brevo;
use Brevo\TransactionalEmails\Requests\SendTransacEmailRequest;
use Brevo\TransactionalEmails\Types\SendTransacEmailRequestBccItem;
use Brevo\TransactionalEmails\Types\SendTransacEmailRequestCcItem;
use Brevo\TransactionalEmails\Types\SendTransacEmailRequestReplyTo;
use Brevo\TransactionalEmails\Types\SendTransacEmailRequestSender;
use Brevo\TransactionalEmails\Types\SendTransacEmailRequestToItem;
use Symfony\Component\Mailer\Exception\TransportException;
use Symfony\Component\Mailer\SentMessage;
use Symfony\Component\Mailer\Transport\AbstractTransport;
use Symfony\Component\Mime\Address;
use Symfony\Component\Mime\Message;
use Symfony\Component\Mime\MessageConverter;

class BrevoTransport extends AbstractTransport
{
    public function __construct(
        private readonly string $apiKey,
    ) {
        parent::__construct();
    }

    protected function doSend(SentMessage $message): void
    {
        $originalMessage = $message->getOriginalMessage();

        if (!$originalMessage instanceof Message) {
            throw new TransportException('A mensagem enviada para o transporte Brevo é inválida.');
        }

        $email = MessageConverter::toEmail($originalMessage);

        $request = new SendTransacEmailRequest([
            'sender'      => $this->buildSender($email->getFrom()),
            'to'          => $this->mapRecipients($email->getTo(), SendTransacEmailRequestToItem::class),
            'cc'          => $this->mapRecipients($email->getCc(), SendTransacEmailRequestCcItem::class),
            'bcc'         => $this->mapRecipients($email->getBcc(), SendTransacEmailRequestBccItem::class),
            'replyTo'     => $this->buildReplyTo($email->getReplyTo()),
            'subject'     => $email->getSubject(),
            'htmlContent' => $email->getHtmlBody(),
            'textContent' => $email->getTextBody(),
        ]);

        (new Brevo($this->apiKey))->transactionalEmails->sendTransacEmail($request);
    }

    public function __toString(): string
    {
        return 'brevo';
    }

    /**
     * @param array<Address> $addresses
     */
    private function buildSender(array $addresses): ?SendTransacEmailRequestSender
    {
        if ($addresses === []) {
            return null;
        }

        $address = $addresses[0];

        return new SendTransacEmailRequestSender([
            'email' => $address->getAddress(),
            'name'  => $address->getName() ?: null,
        ]);
    }

    /**
     * @param array<Address> $addresses
     *
     * @return array<int, SendTransacEmailRequestToItem|SendTransacEmailRequestCcItem|SendTransacEmailRequestBccItem>|null
     */
    private function mapRecipients(array $addresses, string $recipientType): ?array
    {
        if ($addresses === []) {
            return null;
        }

        return array_map(static fn (Address $address) => new $recipientType([
            'email' => $address->getAddress(),
            'name'  => $address->getName() ?: null,
        ]), $addresses);
    }

    /**
     * @param array<Address> $addresses
     */
    private function buildReplyTo(array $addresses): ?SendTransacEmailRequestReplyTo
    {
        if ($addresses === []) {
            return null;
        }

        $address = $addresses[0];

        return new SendTransacEmailRequestReplyTo([
            'email' => $address->getAddress(),
            'name'  => $address->getName() ?: null,
        ]);
    }
}
